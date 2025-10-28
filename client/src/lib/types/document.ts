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
