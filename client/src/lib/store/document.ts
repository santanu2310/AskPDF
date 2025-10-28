import { writable } from 'svelte/store';

export const uploadedDocumentId = writable<string | null>(null);

// Store uploaded document ID
export const setUploadedDocumentId = (docId: string) => {
	uploadedDocumentId.set(docId);
};

// Clear uploaded document ID
export const clearUploadedDocumentId = () => {
	uploadedDocumentId.set(null);
};
