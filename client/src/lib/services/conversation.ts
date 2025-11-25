import { get } from 'svelte/store';
import { authRequest, CONVERSATION_ENDPOINTS } from './api';
import { uploadedDocumentId } from '$lib/store/document';
import { currentConversation, conversations } from '$lib/store/conversation';
import type { MessagePayload, MessageResponse, Conversation } from '$lib/types/conversation';
import { mapMessageResponse, mapConversation } from '$lib/types/conversation';
import { indexedDbService } from './indexedDb';

export async function sendMessage(
	message: string,
	convId: string | null = null
): Promise<MessageResponse> {
	const docId = get(uploadedDocumentId);

	if (!docId && !convId) {
		throw new Error('No document ID and conv found to send message.');
	}

	const payload: MessagePayload = {
		temp_id: new Date().getTime().toString(),
		conv_id: convId,
		message: message,
		file_id: docId
	};

	const response = await authRequest.post(CONVERSATION_ENDPOINTS.SEND_MESSAGE, payload);
	console.log('server response for message', response.data);

	return mapMessageResponse(response.data);
}

export async function syncConversations(): Promise<Conversation[]> {
	const localConversations = (await indexedDbService.getAllRecords(
		'conversation'
	)) as Conversation[];

	const conversationsMap = new Map(localConversations.map((conv) => [conv.id, conv]));
	conversations.set(conversationsMap);

	// Find the last modification date from local conversations
	let lastSyncDate = new Date(0).toISOString();
	if (localConversations.length > 0) {
		lastSyncDate = localConversations.reduce((max, conv) => {
			const convDate = new Date(conv.updatedAt);
			return convDate > new Date(max) ? conv.updatedAt : max;
		}, lastSyncDate);
	}

	const response = await authRequest.get(CONVERSATION_ENDPOINTS.GET_ALL_CHAT, {
		params: {
			last_sync_date: lastSyncDate
		}
	});

	const serverConversations = response.data.map(mapConversation) as Conversation[];
	console.log('serverConversations', serverConversations);

	// Merge server conversations with local ones, then update IndexedDB and the store
	if (serverConversations.length > 0) {
		const conversationsToUpsert = serverConversations.map((serverConv) => {
			const localConv = get(conversations).get(serverConv.id);
			if (localConv) {
				const {
					messages: serverMessages,
					documents: serverDocuments,
					...restServerConv
				} = serverConv;
				return { ...localConv, ...restServerConv };
			}
			return serverConv;
		});

		console.log('conversationsToUpsert', conversationsToUpsert);

		await indexedDbService.batchUpsert('conversation', conversationsToUpsert);
		conversations.update((convsMap) => {
			conversationsToUpsert.forEach((conv) => {
				convsMap.set(conv.id, conv);
			});
			return new Map(convsMap);
		});
	}

	return Array.from(get(conversations).values());
}

export async function updateConversation(conv_id: string, lastUpdated: string) {
	try {
		const response = await authRequest.get(CONVERSATION_ENDPOINTS.GET_CHAT(conv_id), {
			params: {
				last_updated: lastUpdated
			}
		});
		console.log('response', response.data);

		if (
			response.data &&
			response.data.messages.length > 0 &&
			Object.keys(response.data).length > 0
		) {
			console.log('conversation response :', response.data);
			const updatedConversation = mapConversation(response.data) as Conversation;

			console.log('updatedConversation', updatedConversation);
			await indexedDbService.updateRecord('conversation', updatedConversation);

			conversations.update((convsMap) => {
				convsMap.set(updatedConversation.id, updatedConversation);
				return new Map(convsMap);
			});
		}
	} catch (error) {
		console.error('Failed to check for conversation updates:', error);
	}
}

export async function changeConvTitle(id: string, title: string): Promise<void> {
	try {
		const payload = { id, title };
		console.log('payload : ', payload);
		// const response = await authRequest.put(CONVERSATION_ENDPOINTS.GET_CHAT(id), payload);

		const response = await authRequest({
			method: 'put',
			url: CONVERSATION_ENDPOINTS.GET_CHAT(id),
			data: payload
		});
		console.log('updatedConversation for title update : ', response.data);

		const conversationUpdate = mapConversation(response.data) as Conversation;

		const currentConvs = get(conversations);
		const existingConversation = currentConvs.get(id);

		if (!existingConversation) {
			console.error(
				`Conversation with id ${id} not found locally. Storing server response directly.`
			);
			// Fallback to storing the partial data from server if local copy is missing
			await indexedDbService.updateRecord('conversation', conversationUpdate);
			conversations.update((convsMap) => {
				convsMap.set(conversationUpdate.id, conversationUpdate);
				return new Map(convsMap);
			});
			return;
		}

		// Merge the existing conversation with the partial update from the server
		const mergedConversation = { ...existingConversation, ...conversationUpdate };

		// Save the merged conversation to preserve messages and documents
		await indexedDbService.updateRecord('conversation', mergedConversation);

		conversations.update((convsMap) => {
			convsMap.set(mergedConversation.id, mergedConversation);
			return new Map(convsMap);
		});
	} catch (error) {
		console.error(`Failed to update title for conversation ${id}:`, error);
		throw error;
	}
}
