import { writable, get } from 'svelte/store';
import type { Conversation, Message } from '$lib/types/conversation';
import { mapConversation, mapMessage } from '$lib/types/conversation';

export const conversations = writable<Map<string, Conversation>>(new Map());
export const currentConversation = writable<string | null>(null);

/**
 * Adds a new conversation to the store.
 * @param conversation - The conversation to add.
 */
export function addConversation(conversation: Conversation) {
	conversations.update((convsMap) => {
		if (!convsMap.has(conversation.id)) {
			convsMap.set(conversation.id, conversation);
			return new Map(convsMap);
		}
		return convsMap;
	});
}

/**
 * Adds an array of messages to a conversation.
 * @param conversationId - The ID of the conversation to update.
 * @param messageList - The array of messages to add.
 */
export function addMessageToConversation(conversationId: string, messageList: Message[]) {
	let newConv: Conversation | undefined;
	// Update the conversation in the main map
	conversations.update((convsMap) => {
		const conversation = convsMap.get(conversationId);
		if (conversation) {
			const existingMessageIds = new Set(conversation.messages.map((m) => m.id));
			const newMessages = messageList.filter((m) => !existingMessageIds.has(m.id));

			if (newMessages.length > 0) {
				const updatedConversation = {
					...conversation,
					messages: [...conversation.messages, ...newMessages]
				};
				newConv = updatedConversation;
				convsMap.set(conversationId, updatedConversation);
				// Return a new map to trigger reactivity
				return new Map(convsMap);
			}
		}
		return convsMap;
	});
	return newConv;
}
