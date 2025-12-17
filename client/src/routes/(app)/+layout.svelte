<script lang="ts">
	import { onMount } from 'svelte';
	import { user } from '$lib/store/user';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import icon from '$lib/assets/icon.png';
	import { conversations, currentConversation } from '$lib/store/conversation';
	import { syncConversations } from '$lib/services/conversation';
	import { changeConvTitle, deleteConversation } from '$lib/services/conversation';
	import Conversation from '$lib/components/Conversation.svelte';

	// Theme state. Defaults to false (light mode).
	let isDarkMode = $state(false);
	let isLoading = $state(true);

	let chatTitle = $state<string | undefined>(undefined);

	// Edit Popup State
	let isEditPopupOpen = $state(false);
	let isSidebar = $state(false);
	let editingConvDetails: { id: string; title: string } | null = $state(null);
	let deleteConvId: string | null = $state(null);
	let editedConvTitle = $state('');

	// A reference to the menu container in Conversation.svelte. This will be null initially,
	// and will be set when a Conversation component is mounted.
	// Since Conversation.svelte now handles its own menu state and click outside,
	// this variable might not be needed here directly unless the layout needs to interact with it.
	// For now, let's keep it minimal for the layout's specific needs (edit popup).
	// If the menu itself is still in layout, this will be needed.
	// But the menu is inside Conversation.svelte, so the menuContainer is local to Conversation.svelte.
	// Therefore, handleClickOutside here only needs to manage the layout's popup, if any.
	// However, the original prompt from the user mentioned "the popup menue goes out"
	// which referred to the small menu. So, the original handleClickOutside was correct for the menu.
	// Let's re-add the menu's handling in Conversation.svelte.

	onMount(async () => {
		// Check for saved theme preference in localStorage on component mount.
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme === 'dark') {
			isDarkMode = true;
		} else if (savedTheme === 'light') {
			isDarkMode = false;
		} else {
			// If no theme is saved, respect the user's system preference.
			isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
		}

		// Apply the 'dark' class to the document root based on initial state.
		updateThemeClass(isDarkMode);
		if (!$user) {
			isLoading = false;
			return;
		}
		await syncConversations();
		isLoading = false;
	});

	$effect(() => {
		let chatId = page.params.chatId;
		if (chatId == 'new' || chatId == undefined) {
			chatTitle = undefined;
		} else {
			chatTitle = $conversations.get(chatId)?.title;
		}
	});

	// --- Theme Management ---
	function updateThemeClass(isDark: boolean) {
		const root = document.documentElement;
		if (isDark) {
			root.classList.add('dark');
		} else {
			root.classList.remove('dark');
		}
	}

	function toggleTheme() {
		isDarkMode = !isDarkMode;
		updateThemeClass(isDarkMode);
		localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
	}

	// --- Edit Popup Management ---
	function openEditPopup(details: { id: string; title: string }) {
		editingConvDetails = details;
		editedConvTitle = details.title;
		isEditPopupOpen = true;
	}
	function openDeletePopup(id: string) {
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

<div
	class:dark={isDarkMode}
	class="flex h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]"
	style="background-image:radial-gradient(circle at 15% 100%,var(--gradient-accent) 0%,var(--bg-primary) 60%"
>
	<!-- Collapsible Sidebar -->
	<aside
		class=" pt-4 {isSidebar
			? 'w-64'
			: 'lg:w-16'} w-0 fixed left-0 top-0 z-10 flex h-full flex-col bg-[var(--bg-secondary)] backdrop-blur-lg border-r border-[var(--border-primary)] transition-all duration-300 ease-in-out"
	>
		<div class="flex h-16 items-center rounded-lg overflow-hidden transition-all duration-300 p-2">
			<div class="group/icon h-10 w-12 flex items-center justify-center flex-shrink-0">
				<img
					src={icon}
					class="{isSidebar ? '' : 'group-hover/icon:hidden'} w-8 h-8 object-contain"
					alt=""
				/>
				{#if !isSidebar}
					<button
						class="w-8 h-auto aspect-square group-hover/icon:flex hidden justify-center items-center text-xl cursor-e-resize opacity-80"
						onclick={() => (isSidebar = true)}
						aria-label="Open nav"
					>
						<i class="ri-layout-right-line"></i>
					</button>
				{/if}
			</div>
			{#if isSidebar}
				<div class="pl-1 flex grow items-center justify-between">
					<span
						class=" text-lg font-bold whitespace-nowrap opacity-100 transition-opacity duration-300"
						>AskPDF</span
					>
					<button
						class="w-auto h-10 aspect-square text-xl cursor-w-resize opacity-80"
						onclick={() => (isSidebar = false)}
						ontouchend={() => (isSidebar = false)}
						aria-label="Close Nav"
					>
						<i class="ri-layout-left-line"></i></button
					>
				</div>
			{/if}
		</div>

		<nav
			class=" flex flex-col justify-start space-y-4 px-2 py-4 min-h-0"
			style="height: calc(100% - 190px)"
		>
			<!-- New Chat Button -->
			<a
				href="/"
				onclick={() => {
					isSidebar = false;
				}}
				class="flex h-10 items-center rounded-lg overflow-hidden hover:bg-[var(--bg-primary)] text-[var(--text-secondary)] transition-all duration-300"
			>
				<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
					<i class="ri-add-fill text-lg"></i>
				</div>
				{#if isSidebar}
					<span
						class="ml-1 text-sm font-semibold whitespace-nowrap opacity-100 transition-opacity duration-300"
						>New Chat</span
					>
				{/if}
			</a>

			<!-- History Section -->

			{#if isSidebar}
				<div class="flex flex-col grow pt-4 min-h-0">
					<h3
						class="px-2 text-xs font-semibold uppercase text-[var(--text-muted)] opacity-100 transition-opacity duration-300"
					>
						History
					</h3>
					{#if isLoading}
						<ul class="mt-2 space-y-1 animate-pulse">
							<li>
								<p class="w-full h-6 mt-3 block truncate rounded-lg bg-[var(--bg-primary)]"></p>
							</li>
							<li>
								<p class="w-full h-6 mt-2 block truncate rounded-lg bg-[var(--bg-primary)]"></p>
							</li>
						</ul>
					{:else}
						<ul
							class="mt-2 flex flex-col grow overflow-y-auto space-y-1 transition-opacity duration-300"
						>
							{#each Array.from($conversations.values()) as conversation}
								<Conversation
									convId={conversation.id}
									convTitle={conversation.title}
									onEdit={openEditPopup}
									onDelete={openDeletePopup}
									onConvSelect={() => (isSidebar = false)}
								/>
							{/each}
						</ul>
					{/if}
				</div>
			{/if}
		</nav>

		<!-- Bottom Section: Theme Toggle & User -->
		<div class="h-fit px-2 py-4">
			<button
				onclick={toggleTheme}
				aria-label="Toggle theme"
				class="flex h-10 w-full items-center rounded-lg overflow-hidden text-[var(--text-muted)] hover:bg-[var(--bg-primary)] transition-all duration-300"
			>
				<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
					{#if isDarkMode}
						<i class="ri-moon-line"></i>
					{:else}
						<i class="ri-sun-line"></i>
					{/if}
				</div>

				{#if isSidebar}
					<span
						class="ml-1 text-sm font-semibold whitespace-nowrap opacity-100 transition-opacity duration-300"
					>
						{isDarkMode ? 'Light Mode' : 'Dark Mode'}
					</span>
				{/if}
			</button>

			<div
				class="mt-2 flex h-10 w-full cursor-pointer items-center rounded-lg overflow-hidden text-[var(--text-muted)] hover:bg-[var(--bg-primary)] transition-all duration-300"
			>
				{#if $user}
					<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
						<div class="w-auto h-8 aspect-square overflow-hidden rounded-full">
							<img
								src={$user.profilePicUrl}
								alt=""
								referrerpolicy="no-referrer"
								class="h-full w-full object-cover"
							/>
						</div>
					</div>

					{#if isSidebar}
						<span
							class="ml-1 text-sm font-semibold whitespace-nowrap opacity-100 transition-opacity duration-300"
							>{$user.fullName}</span
						>
					{/if}
				{:else}
					<a href="/auth/login" class="h-full w-full flex items-center">
						<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
							<svg
								class="h-6 w-6"
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
						</div>
						<span
							class="ml-1 text-sm font-semibold whitespace-nowrap opacity-0 group-hover/sidebar:opacity-100 transition-opacity duration-300"
							>Login</span
						>
					</a>
				{/if}
			</div>
		</div>
	</aside>

	<!-- Main Content -->
	<main class="flex h-full flex-col flex-1 lg:ml-16 transition-all duration-300 ease-in-out">
		<div class="w-full min-h-14 flex justify-between py-2 px-3 lg:hidden">
			<button
				class="h-full w-auto aspect-square rounded-lg text-lg"
				aria-label="open nav on movbile"
				ontouchend={() => (isSidebar = true)}
				onclick={() => (isSidebar = true)}
			>
				<svg
					width="24"
					height="24"
					viewBox="0 0 20 20"
					fill="currentColor"
					xmlns="http://www.w3.org/2000/svg"
					data-rtl-flip=""
					class="text-token-text-secondary icon-lg mx-2"
					><path
						d="M11.6663 12.6686L11.801 12.6823C12.1038 12.7445 12.3313 13.0125 12.3313 13.3337C12.3311 13.6547 12.1038 13.9229 11.801 13.985L11.6663 13.9987H3.33325C2.96609 13.9987 2.66839 13.7008 2.66821 13.3337C2.66821 12.9664 2.96598 12.6686 3.33325 12.6686H11.6663ZM16.6663 6.00163L16.801 6.0153C17.1038 6.07747 17.3313 6.34546 17.3313 6.66667C17.3313 6.98788 17.1038 7.25586 16.801 7.31803L16.6663 7.33171H3.33325C2.96598 7.33171 2.66821 7.03394 2.66821 6.66667C2.66821 6.2994 2.96598 6.00163 3.33325 6.00163H16.6663Z"
					></path></svg
				>
			</button>

			{#if chatTitle}
				<div class="flex flex-grow justify-center items-center">
					<div class="flex rounded-full w-38 items-center justify-between">
						<span
							class="text-base font-medium whitespace-nowrap overflow-hidden text-ellipsis max-w-[80%]"
							>{chatTitle}</span
						>
						<span class="mx-1"><i class="ri-arrow-down-s-line"></i></span>
					</div>
				</div>
			{/if}
		</div>
		<div class="relative flex flex-grow flex-col w-full min-h-0">
			<!-- Child content will be rendered here -->
			<slot></slot>
		</div>
	</main>

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
					<div
						class="flex justify-end space-x-2 text-sm font-semibold text-[var(--text-secondary)]"
					>
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
					<span class="mb-8 block text-sm font-normal"
						>This will delete all the messages and the document associated with this conversation.</span
					>
					<div
						class="flex justify-end space-x-2 text-sm font-semibold text-[var(--text-secondary)]"
					>
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
</div>
