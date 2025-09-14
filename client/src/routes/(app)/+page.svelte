<script lang="ts">
	import { authRequest, CONVERSATION_ENDPOINTS } from '$lib/services/api';
	import { documentStore, setUploadSession, setUploading, setUploadError } from '$lib/store/document';
	import { goto } from '$app/navigation';
	import axios from 'axios';

	let files: File[] = [];
	let isDragging: boolean = false;
	let errorMessage: string = '';

	// Function to handle file processing and validation
	async function handleFiles(fileList: FileList) {
		errorMessage = '';
		const newFiles = Array.from(fileList);
		const pdfFiles = newFiles.filter((file) => {
			if (file.type === 'application/pdf') {
				return true;
			}
			errorMessage = 'Invalid file type. Please upload PDFs only.';
			return false;
		});

		if (errorMessage === '' && pdfFiles.length > 0) {
			// Only handle the first file for now
			const file = pdfFiles[0];
			files = [file];
			
			try {
				setUploading(true);
				setUploadError(null);

				// Step 1: Get presigned upload URL
				const uploadSessionResponse = await authRequest.post(CONVERSATION_ENDPOINTS.UPLOAD_SESSION, {
					file_name: file.name
				});

				const uploadSession = uploadSessionResponse.data;
				setUploadSession(uploadSession);

				// Step 2: Upload file to presigned URL
				const formData = new FormData();
				
				// Add all fields from the presigned URL response
				Object.entries(uploadSession.fields).forEach(([key, value]) => {
					formData.append(key, value as string);
				});
				
				// Add the file last
				formData.append('file', file);

				await axios.post(uploadSession.url, formData, {
					headers: {
						'Content-Type': 'multipart/form-data'
					}
				});

				// Step 3: Redirect to chat/new
				goto('/chat/new');
				
			} catch (error) {
				console.error('Upload failed:', error);
				setUploadError('Upload failed. Please try again.');
			} finally {
				setUploading(false);
			}
		}
	}

	// Event handler for file input change
	function onInputChange(event: Event) {
		const target = event.target as HTMLInputElement;
		if (!$documentStore.isUploading && target.files) {
			handleFiles(target.files);
		}
	}

	// --- Drag and Drop Handlers ---
	function onDragOver(event: DragEvent) {
		event.preventDefault();
		if (!$documentStore.isUploading && !isDragging) isDragging = true;
	}

	function onDragLeave(event: DragEvent) {
		event.preventDefault();
		isDragging = false;
	}

	function onDrop(event: DragEvent) {
		event.preventDefault();
		isDragging = false;
		if (!$documentStore.isUploading && event.dataTransfer?.files) {
			handleFiles(event.dataTransfer.files);
		}
	}

	// Function to remove a file from the list
	function removeFile(index: number) {
		files = files.filter((_, i) => i !== index);
	}
</script>

<div
	class="antialiased font-sans transition-colors duration-300 bg-[var(--bg-primary)] text-[var(--text-primary)] min-h-screen w-full flex flex-col items-center justify-center p-4"
>
	<div class="w-full max-w-lg">
		<!-- File Upload Container -->
		<div
			class="bg-[var(--bg-secondary)] p-8 rounded-2xl shadow-sm border border-[var(--border-primary)] text-center backdrop-blur-lg"
		>
			<h2 class="text-2xl font-bold text-[var(--text-primary)] mb-2">Upload Your Documents</h2>
			<p class="text-[var(--text-secondary)] mb-6">
				Upload PDF files by clicking or dragging them into the zone below.
			</p>

			<!-- Drop Zone -->
			<label
				for="file-upload"
				class="relative block w-full border-2 border-dashed rounded-xl p-8 transition-colors duration-300"
				class:cursor-pointer={!$documentStore.isUploading}
				class:cursor-not-allowed={$documentStore.isUploading}
				class:opacity-50={$documentStore.isUploading}
				class:border-[var(--text-accent)]={isDragging && !$documentStore.isUploading}
				class:border-[var(--border-secondary)]={!isDragging || $documentStore.isUploading}
				on:dragenter|preventDefault
				on:dragover={onDragOver}
				on:dragleave={onDragLeave}
				on:drop={onDrop}
			>
				<div class="flex flex-col items-center justify-center space-y-4">
					<svg
						class="w-16 h-16 text-[var(--text-muted)]"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M12 16.5V9.75m0 0l-3.75 3.75M12 9.75l3.75 3.75M3 13.5v6c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-6m-16 0V7.5a2.25 2.25 0 012.25-2.25h11.5A2.25 2.25 0 0121 7.5v6"
						/>
					</svg>
					<p class="text-[var(--text-secondary)]">
						<span class="font-semibold text-[var(--text-accent)]">Click to upload</span> or drag and
						drop
					</p>
					<p class="text-xs text-[var(--text-muted)]">PDF files only, up to 10MB</p>
				</div>
				<input
					id="file-upload"
					name="file-upload"
					type="file"
					class="sr-only"
					accept=".pdf"
					disabled={$documentStore.isUploading}
					on:change={onInputChange}
				/>
			</label>

			<!-- Error Message -->
			{#if errorMessage || $documentStore.uploadError}
				<div
					class="mt-4 p-3 text-sm text-[var(--text-error)] bg-[var(--bg-error)] border border-[var(--border-error)] rounded-lg"
				>
					{errorMessage || $documentStore.uploadError}
				</div>
			{/if}

			<!-- Upload Progress -->
			{#if $documentStore.isUploading}
				<div class="mt-4 p-4 bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-lg">
					<div class="flex items-center space-x-3">
						<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[var(--text-accent)]"></div>
						<span class="text-sm text-[var(--text-secondary)]">Uploading file...</span>
					</div>
				</div>
			{/if}
		</div>

		<!-- File List -->
		{#if files.length > 0}
			<div class="mt-8">
				<h3 class="font-semibold text-[var(--text-secondary)] mb-4">Uploaded Files</h3>
				<ul class="space-y-3">
					{#each files as file, index (file.name)}
						<li
							class="flex items-center justify-between bg-[var(--bg-secondary)] p-4 rounded-xl shadow-sm border border-[var(--border-primary)] animate-fade-in backdrop-blur-lg"
						>
							<div class="flex items-center space-x-3 overflow-hidden">
								<svg
									class="w-6 h-6 text-[var(--text-accent)] flex-shrink-0"
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									><path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
									/></svg
								>
								<span class="text-sm text-[var(--text-primary)] truncate" title={file.name}
									>{file.name}</span
								>
							</div>
							<button
								on:click={() => removeFile(index)}
								class="p-1 rounded-full text-[var(--text-muted)] hover:bg-[var(--bg-toggle-hover)] hover:text-[var(--text-primary)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--ring-secondary)]"
							>
								<svg
									class="w-5 h-5"
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									><path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M6 18L18 6M6 6l12 12"
									/></svg
								>
							</button>
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>
</div>

<style>
	/* Simple fade-in animation for file list */
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	.animate-fade-in {
		animation: fadeIn 0.3s ease-out forwards;
	}
</style>
