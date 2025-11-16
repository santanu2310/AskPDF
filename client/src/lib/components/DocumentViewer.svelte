<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { indexedDbService } from '$lib/services/indexedDb';
	import { authRequest, CONVERSATION_ENDPOINTS } from '$lib/services/api';
	import type { Document } from '$lib/types/document';
	import { PdfViewer } from '@santanu2310/svelte-pdf-kit';
	import { uploadedDocumentId } from '$lib/store/document';
	import LazerLine from './LazerLine.svelte';

	interface Props {
		documentId: string;
		isTemp: boolean;
	}

	let { documentId }: Props = $props();
	let pdfUrl = $state<string>('');
	let status: 'success' | 'failed' | 'processing' = $state('processing');
	let error = $state<string>('');
	let pollingActive = true;

	function delay(ms: number) {
		return new Promise((resolve) => setTimeout(resolve, ms));
	}
	async function pollFileStatus(interval = 3000, maxAttempts = 50) {
		let attempts = 0;

		while (attempts < maxAttempts && pollingActive) {
			attempts++;
			console.log(`Polling attempt ${attempts}...`);

			try {
				const response = await authRequest.get(CONVERSATION_ENDPOINTS.FILE_STATUS(documentId));

				if (response.data && response.data.status === 'success') {
					status = response.data.status;
					if (response.data.status != 'processing') return;
				}

				await delay(interval);
			} catch (error: any) {
				console.error('Error during polling:', error.message);
				await delay(interval);
			}
		}

		// If the loop finishes without the condition being met
		throw new Error(`Polling failed after ${maxAttempts} attempts.`);
	}
	onMount(async () => {
		try {
			const storeName = 'document';
			const document = (await indexedDbService.getRecord(
				storeName,
				$uploadedDocumentId as string
			)) as Document;
			console.log(document);
			if (!document) return;

			await pollFileStatus();

			if (document?.data) {
				pdfUrl = URL.createObjectURL(document.data);
			} else {
				error = 'Document not found';
			}
		} catch (err) {
			error = 'Failed to load document';
		}
	});
	onDestroy(() => {
		pollingActive = false;
	});
</script>

{#if status == 'processing'}
	<div class="flex items-center justify-center p-8">
		<LazerLine />
	</div>
{:else if error}
	<div
		class="p-4 text-[var(--text-error)] bg-[var(--bg-error)] border border-[var(--border-error)] rounded-lg"
	>
		{error}
	</div>
{:else if pdfUrl}
	<PdfViewer url={pdfUrl} />
{/if}
