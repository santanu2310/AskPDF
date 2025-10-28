import axios from 'axios';
import { goto } from '$app/navigation';
import { setUploadedDocumentId } from '$lib/store/document';
import { authRequest, CONVERSATION_ENDPOINTS } from '$lib/services/api';
import type { Document } from '$lib/types/document';
import { indexedDbService } from './indexedDb';

export async function handleFile(
	selectedFile: File
): Promise<{ success: boolean; error?: string }> {
	if (selectedFile.type !== 'application/pdf') {
		return { success: false, error: 'Invalid file type. Please upload PDFs only.' };
	}

	try {
		const uploadSessionResponse = await authRequest.post(CONVERSATION_ENDPOINTS.UPLOAD_SESSION, {
			file_name: selectedFile.name
		});

		const uploadSession = uploadSessionResponse.data;

		const formData = new FormData();
		Object.entries(uploadSession.fields).forEach(([key, value]) => {
			formData.append(key, value as string);
		});
		formData.append('file', selectedFile);

		await axios.post(uploadSession.url, formData);

		const document: Document = {
			id: uploadSession.doc_id,
			data: selectedFile
		};

		const storeName = 'document';
		await indexedDbService.addRecord(storeName, document);

		setUploadedDocumentId(uploadSession.doc_id);
		goto('/chat/new');

		return { success: true };
	} catch (error) {
		return { success: false, error: 'Upload failed. Please try again.' };
	}
}
