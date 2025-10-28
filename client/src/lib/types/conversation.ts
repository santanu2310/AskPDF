interface Citation {
	text: string;
	source: string;
}

export interface Message {
	id: string;
	text: string;
	citations?: Citation[];
	conversationId: string;
	role: 'user' | 'assistant';
	timeStamp: string;
}

export interface Conversation {
	id: string;
	title: string;
	messages: Array<Message>;
	documents: Array<string>;
	createdAt: string;
}

export function mapMessage(serverMessage: any): Message {
	return {
		id: serverMessage.id,
		text: serverMessage.text,
		citations: serverMessage.citations,
		conversationId: serverMessage.conversation_id,
		role: serverMessage.role,
		timeStamp: serverMessage.time_stamp
	};
}

export function mapConversation(serverConversation: any): Conversation {
	return {
		id: serverConversation.id,
		title: serverConversation.title,
		messages: serverConversation.messages?.map(mapMessage) || [],
		documents: serverConversation.documents || [],
		createdAt: serverConversation.created_at
	};
}

export interface MessagePayload {
	temp_id: string;
	conv_id: string | null;
	message: string;
	file_id: string;
}

export interface MessageResponse {
    conversationId: string;
    fileId?: string;
    userMessage: Message;
    assistantMessage: Message;
    createdAt?: string;
}

export function mapMessageResponse(serverResponse: any): MessageResponse {
    return {
        conversationId: serverResponse.conversation_id,
        fileId: serverResponse.file_id,
        userMessage: mapMessage(serverResponse.user_message),
        assistantMessage: mapMessage(serverResponse.assistant_message),
        createdAt: serverResponse.created_at
    };
}