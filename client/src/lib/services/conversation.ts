import { get } from 'svelte/store';
import { authRequest, CONVERSATION_ENDPOINTS } from './api';
import { uploadedDocumentId } from '$lib/store/document';
import { currentConversation, conversations } from '$lib/store/conversation';
import type { MessagePayload, MessageResponse, Conversation } from '$lib/types/conversation';
import { mapMessageResponse } from '$lib/types/conversation';
import { indexedDbService } from './indexedDb';

export async function sendMessage(message: string): Promise<MessageResponse> {
	const conv = get(currentConversation);
	const docId = get(uploadedDocumentId);

	if (!docId) {
		throw new Error('No document ID found to send message.');
	}

	const payload: MessagePayload = {
		temp_id: new Date().getTime().toString(),
		conv_id: conv,
		message: message,
		file_id: docId
	};

	const response = await authRequest.post(CONVERSATION_ENDPOINTS.SEND_MESSAGE, payload);

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
			const convDate = new Date(conv.updated_at);
			return convDate > new Date(max) ? conv.updated_at : max;
		}, lastSyncDate);
	}

	const response = await authRequest.get(CONVERSATION_ENDPOINTS.GET_ALL_CHAT, {
		params: {
			last_sync_date: lastSyncDate
		}
	});

	const serverConversations = response.data as Conversation[];

	// Merge server conversations with local ones, then update IndexedDB and the store
	if (serverConversations.length > 0) {
		const conversationsToUpsert = serverConversations.map((serverConv) => {
			const localConv = get(conversations).get(serverConv.id);
			if (localConv) {
				return { ...localConv, ...serverConv };
			}
			return serverConv;
		});

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
