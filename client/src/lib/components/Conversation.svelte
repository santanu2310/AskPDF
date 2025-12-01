<script lang="ts">
	interface Props {
		convId: string;
		convTitle: string;
		onEdit: (details: { id: string; title: string }) => void;
		onDelete: (id: string) => void;
	}
	let { convId, convTitle, onEdit, onDelete }: Props = $props();

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
</script>

<svelte:window on:click={handleClickOutside} />

<li class="group w-full flex items-center justify-between rounded-lg hover:bg-[var(--bg-primary)]">
	<a href="/chat/{convId}" class="truncate p-2 text-sm text-[var(--text-secondary)] flex-grow">
		{convTitle}
	</a>

	<div class="relative flex-shrink-0" bind:this={menuContainer}>
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
								// TODO: Implement Pin logic
								console.log('Pinning conversation:', convId);
								close();
							}}
						>
							<i class="ri-pushpin-line"></i> Pin
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
