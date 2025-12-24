<script lang="ts">
	import { goto } from '$app/navigation';
	import { changeConvTitle, deleteConversation } from '$lib/services/conversation';

	// Edit Popup State
	let isEditPopupOpen = $state(false);
	let editingConvDetails: { id: string; title: string } | null = $state(null);
	let deleteConvId: string | null = $state(null);
	let editedConvTitle = $state('');

	export function openEditPopup(details: { id: string; title: string }) {
		editingConvDetails = details;
		editedConvTitle = details.title;
		isEditPopupOpen = true;
	}

	export function openDeletePopup(id: string) {
		deleteConvId = id;
		isEditPopupOpen = true;
	}

	function closeEditPopup() {
		isEditPopupOpen = false;
		deleteConvId = null;
		editingConvDetails = null;
	}

	async function handleUpdateTitle() {
		if (!editingConvDetails) return;
		await changeConvTitle(editingConvDetails.id, editedConvTitle);
		closeEditPopup();
	}

	async function handleDelete() {
		if (!deleteConvId) return;
		await deleteConversation(deleteConvId);
		closeEditPopup();
		goto('/');
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && isEditPopupOpen) {
			closeEditPopup();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />
<!-- Edit Conversation Title Popup -->
{#if isEditPopupOpen}
	<div
		class="fixed inset-0 bg-[var(--bg-secondary)] backdrop-blur-lg flex items-center justify-center z-50"
		onclick={closeEditPopup}
		role="button"
		tabindex="0"
		onkeydown={(e) => {
			if (e.key === 'Esc') closeEditPopup();
		}}
	>
		<div
			class="bg-[var(--bg-primary)] p-6 rounded-lg shadow-lg w-xl"
			onclick={(e) => e.stopPropagation()}
			role="button"
			tabindex="0"
			onkeydown={(e) => {}}
		>
			{#if editingConvDetails}
				<h3 class="text-xl font-medium mb-12 text-[var(--text-primary)]">
					Edit Conversation Title
				</h3>
				<input
					type="text"
					class="w-full p-3.5 mb-8 rounded-md text-base bg-[var(--bg-secondary)] text-[var(--text-primary)] border border-[var(--border-primary)] focus:outline-1 outline-[var(--gradient-accent)]"
					bind:value={editedConvTitle}
				/>
				<div class="flex justify-end space-x-2 text-sm font-semibold text-[var(--text-secondary)]">
					<button
						class="px-4 py-2 rounded-md hover:text-[var(--text-primary)]"
						onclick={closeEditPopup}
					>
						Cancel
					</button>
					<button
						class="px-4 py-2 rounded-md hover:text-[var(--text-primary)]"
						onclick={handleUpdateTitle}
					>
						Update
					</button>
				</div>
			{:else}
				<h3 class="text-xl font-medium mb-10 text-[var(--text-primary)]">Delete chat?</h3>
				<span class="mb-8 block text-sm font-normal text-[var(--text-secondary)]"
					>This will delete all the messages and the document associated with this conversation.</span
				>
				<div class="flex justify-end space-x-2 text-sm font-semibold text-[var(--text-secondary)]">
					<button
						class="px-4 py-2 rounded-md hover:text-[var(--text-primary)]"
						onclick={closeEditPopup}
					>
						Cancel
					</button>
					<button
						class="px-4 py-2 rounded-md hover:text-[var(--text-primary)]"
						onclick={handleDelete}
					>
						Delete
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
