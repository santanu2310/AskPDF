<script lang="ts">
	import { goto } from '$app/navigation';
	import { togglePinConv } from '$lib/services/conversation';

	interface Props {
		convId: string;
		convTitle: string;
		pinned: boolean;
		onEdit: (details: { id: string; title: string }) => void;
		onDelete: (id: string) => void;
		onConvSelect: () => void;
	}
	let { convId, convTitle, pinned, onEdit, onDelete, onConvSelect }: Props = $props();

	let menuContainer: HTMLElement;
	let isMenuOpen = $state(false);

	function close() {
		isMenuOpen = false;
	}

	function handleClickOutside(event: MouseEvent) {
		if (isMenuOpen && menuContainer && !menuContainer.contains(event.target as Node)) {
			close();
		}
	}

	function handleConversationClick(event: MouseEvent) {
		event.preventDefault();
		if (onConvSelect) {
			onConvSelect();
		}
		goto(`/chat/${convId}`);
	}
</script>

<svelte:window on:click={handleClickOutside} />

<li class="group w-full flex items-center justify-between rounded-lg hover:bg-[var(--bg-primary)]">
	<a
		href="/chat/{convId}"
		onclick={handleConversationClick}
		class="truncate p-2 text-sm text-[var(--text-secondary)] flex-grow"
	>
		{convTitle}
	</a>

	{#if pinned}
		<i class="ri-pushpin-2-line mr-2.5 md:group-hover:hidden"></i>
	{/if}

	<div class="relative flex-shrink-0 hidden md:flex" bind:this={menuContainer}>
		<button
			aria-label="More options"
			class="w-auto h-7 m-1 aspect-square items-center justify-center rounded-md hover:bg-[var(--bg-secondary)] {isMenuOpen
				? 'block'
				: 'hidden group-hover:flex'}"
			onclick={() => (isMenuOpen = !isMenuOpen)}
		>
			<i class="ri-more-2-fill"></i>
		</button>

		{#if isMenuOpen}
			<div
				class="absolute top-full right-0 mt-1 w-36 bg-[var(--bg-primary)] text-[var(--text-secondary)] border border-[var(--border-primary)] rounded-md shadow-lg z-20"
			>
				<ul class="py-1">
					<li>
						<button
							class="w-full text-left pl-4 py-1.5 text-sm hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]"
							onclick={() => {
								togglePinConv(convId);
								close();
							}}
						>
							{#if pinned}
								<i class="ri-unpin-line"></i> unpin
							{:else}
								<i class="ri-pushpin-line"></i> Pin
							{/if}
						</button>
					</li>
					<li>
						<button
							class="w-full text-left pl-4 py-1.5 text-sm hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]"
							onclick={() => {
								onEdit({ id: convId, title: convTitle });
								close();
							}}
						>
							<i class="ri-pencil-line"></i> Edit
						</button>
					</li>
					<li>
						<button
							class="w-full text-left pl-4 py-1.5 text-sm hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]"
							onclick={() => {
								onDelete(convId);
								close();
							}}
						>
							<i class="ri-delete-bin-4-line"></i> Delete
						</button>
					</li>
				</ul>
			</div>
		{/if}
	</div>
</li>
