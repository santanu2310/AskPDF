export interface UploadSession {
	temp_id?: string;
	doc_id?: string;
	url: string;
	fields: Record<string, any>;
}

export interface DocumentState {
	uploadSession: UploadSession | null;
	isUploading: boolean;
	uploadError: string | null;
}

export interface Document {
	id: string;
	data: Blob;
}

export interface DocumentObject {
	id: string;
	title: string;
	createdAt: string;
}

export function mapDcoumentResponse(serverConversation: any): DocumentObject {
	return {
		id: serverConversation.id,
		title: serverConversation.title,
		createdAt: serverConversation.updated_at
	};
}
