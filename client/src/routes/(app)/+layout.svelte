<script lang="ts">
	import { onMount } from 'svelte';
	import { user } from '$lib/store/user';
	import icon from '$lib/assets/icon.png';
	import type { Conversation } from '$lib/types/conversation';
	import { conversations } from '$lib/store/conversation';
	import { syncConversations } from '$lib/services/conversation';

	// Theme state. Defaults to false (light mode).
	let isDarkMode = $state(false);
	let isLoading = $state(true);

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
		console.log($conversations);
		isLoading = false;
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
</script>

<div
	class:dark={isDarkMode}
	class="flex h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]"
>
	<!-- Collapsible Sidebar -->
	<aside
		class="group pt-4 w-16 fixed left-0 top-0 z-10 flex h-full flex-col bg-[var(--bg-secondary)] backdrop-blur-lg border-r border-[var(--border-primary)] transition-all duration-300 ease-in-out hover:w-64"
	>
		<div class="flex h-16 items-center rounded-lg overflow-hidden transition-all duration-300 p-2">
			<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
				<img src={icon} alt="" class="w-8 h-8 object-contain" />
			</div>
			<span
				class="ml-1 text-lg font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300"
				>AskPDF</span
			>
		</div>

		<nav
			class=" flex flex-col justify-start space-y-4 px-2 py-4 min-h-0"
			style="height: calc(100% - 190px)"
		>
			<!-- New Chat Button -->
			<a
				href="/"
				class="flex h-10 items-center rounded-lg overflow-hidden hover:bg-[var(--bg-primary)] text-[var(--text-secondary)] transition-all duration-300"
			>
				<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
					<i class="ri-add-fill text-lg"></i>
				</div>
				<span
					class="ml-1 text-sm font-semibold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300"
					>New Chat</span
				>
			</a>

			<!-- History Section -->
			<div class="flex flex-col grow pt-4 min-h-0">
				<h3
					class="px-2 text-xs font-semibold uppercase text-[var(--text-muted)] hidden group-hover:block"
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
					<ul class="mt-2 hidden flex-col grow overflow-y-scroll space-y-1 group-hover:flex">
						{#each Array.from($conversations.values()) as conversation}
							<li>
								<a
									href="/chat/{conversation.id}"
									class="block truncate rounded-lg p-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-primary)]"
									>{conversation.title}
								</a>
							</li>
						{/each}
					</ul>
				{/if}
			</div>
		</nav>

		<!-- Bottom Section: Theme Toggle & User -->
		<div class="h-fit px-2 py-4">
			<button
				on:click={toggleTheme}
				aria-label="Toggle theme"
				class="flex h-10 w-full items-center rounded-lg overflow-hidden text-[var(--text-muted)] hover:bg-[var(--bg-toggle-hover)] transition-all duration-300"
			>
				<div class="h-10 w-12 flex items-center justify-center flex-shrink-0">
					{#if isDarkMode}
						<i class="ri-moon-line"></i>
					{:else}
						<i class="ri-sun-line"></i>
					{/if}
				</div>
				<span
					class="ml-1 text-sm font-semibold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300"
				>
					{isDarkMode ? 'Light Mode' : 'Dark Mode'}
				</span>
			</button>

			<div
				class="mt-2 flex h-10 w-full cursor-pointer items-center rounded-lg overflow-hidden text-[var(--text-muted)] hover:bg-[var(--bg-toggle-hover)] transition-all duration-300"
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
					<span
						class="ml-1 text-sm font-semibold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300"
						>{$user.fullName}</span
					>
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
							class="ml-1 text-sm font-semibold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300"
							>Login</span
						>
					</a>
				{/if}
			</div>
		</div>
	</aside>

	<!-- Main Content -->
	<main class="flex-1 ml-16 transition-all duration-300 ease-in-out">
		<div class="relative flex h-full flex-col items-center justify-center w-full">
			<!-- Child content will be rendered here -->
			<slot></slot>
		</div>
	</main>
</div>
