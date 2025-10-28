import { get } from 'svelte/store';
import { authRequest, CONVERSATION_ENDPOINTS } from './api';
import { uploadedDocumentId } from '$lib/store/document';
import { currentConversation } from '$lib/store/conversation';
import type { MessagePayload, MessageResponse } from '$lib/types/conversation';
import { mapMessageResponse } from '$lib/types/conversation';

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
