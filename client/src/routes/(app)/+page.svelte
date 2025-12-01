<script lang="ts">
	import { handleFile } from '$lib/services/document';

	let files = $state<FileList | undefined>(undefined);
	let isUploading = $state(false);
	let errorMessage = $state('');
	let fileInput: HTMLInputElement;

	$effect(() => {
		if (files?.[0] && !isUploading) {
			uploadFile(files[0]);
		}
	});

	async function uploadFile(file: File) {
		isUploading = true;
		errorMessage = '';

		const result = await handleFile(file);

		if (!result.success) {
			errorMessage = result.error || 'Upload failed';
		}

		files = undefined;
		isUploading = false;
		if (fileInput) {
			fileInput.value = ''; // Clear the file input
		}
	}
</script>

<div
	class="antialiased font-sans transition-colors duration-300 text-[var(--text-primary)] min-h-screen w-full flex flex-col items-center justify-center p-4"
>
	<div class="w-full max-w-lg">
		<div
			class="bg-[var(--bg-secondary)] p-8 rounded-2xl shadow-sm border border-[var(--border-primary)] text-center backdrop-blur-lg"
		>
			<h2 class="text-2xl font-bold text-[var(--text-primary)] mb-2">Upload Your Documents</h2>
			<p class="text-[var(--text-secondary)] mb-6">
				Upload PDF files by clicking or dragging them into the zone below.
			</p>

			<label
				for="file-upload"
				class="relative block w-full border-2 border-dashed rounded-xl p-8 transition-colors duration-300"
				class:cursor-pointer={!isUploading}
				class:cursor-not-allowed={isUploading}
				class:opacity-50={isUploading}
				class:border-[var(--border-secondary)]={!isUploading}
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
					type="file"
					class="sr-only"
					accept=".pdf"
					disabled={isUploading}
					bind:files
					bind:this={fileInput}
				/>
			</label>

			{#if errorMessage}
				<div
					class="mt-4 p-3 text-sm text-[var(--text-error)] bg-[var(--bg-error)] border border-[var(--border-error)] rounded-lg"
				>
					{errorMessage}
				</div>
			{/if}

			{#if isUploading}
				<div
					class="mt-4 p-4 bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-lg"
				>
					<div class="flex items-center space-x-3">
						<div
							class="animate-spin rounded-full h-5 w-5 border-b-2 border-[var(--text-accent)]"
						></div>
						<span class="text-sm text-[var(--text-secondary)]">Uploading file...</span>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
