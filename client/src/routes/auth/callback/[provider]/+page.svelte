<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { user } from '$lib/store/user';
	import { exchangeCoceForToken } from '$lib/services/auth';
	import type { AuthProvider } from '$lib/types/user';

	let isProcessing = $state(true);
	let errorMessage = $state('');

	onMount(() => {
		handleOAuthCallback();
	});

	async function handleOAuthCallback() {
		try {
			const code = $page.url.searchParams.get('code');
			const state = $page.url.searchParams.get('state');
			const error = $page.url.searchParams.get('error');
			const provider: string | undefined = $page.params.provider;

			if (error) {
				errorMessage = 'Authentication failed. Please try again.';
				isProcessing = false;
				return;
			}

			if (!code || !state || !provider) {
				errorMessage = 'Invalid authentication response.';
				isProcessing = false;
				return;
			}
			const result = await exchangeCoceForToken(code, state, provider as AuthProvider);
			user.set(result);
			goto('/');
		} catch (error) {
			errorMessage = 'Something went wrong. Please try again.';
			isProcessing = false;
		}
	}
</script>

<main
	style="background: var(--bg-primary); background-image: radial-gradient(ellipse 80% 80% at 50% -20%, var(--gradient-accent), var(--gradient-transparent));"
	class="relative flex flex-col items-center justify-center min-h-screen w-full transition-colors duration-300"
>
	<div
		style="background: var(--bg-secondary); border-color: var(--border-primary);"
		class="w-full max-w-md p-8 space-y-8 backdrop-blur-lg border rounded-2xl shadow-2xl text-center"
	>
		{#if isProcessing}
			<div class="space-y-6">
				<!-- Loading Animation -->
				<div class="flex justify-center">
					<div
						style="border-color: var(--text-accent); border-top-color: transparent;"
						class="w-12 h-12 border-4 rounded-full animate-spin"
					></div>
				</div>

				<div class="space-y-2">
					<h2 style="color: var(--text-primary);" class="text-xl font-semibold">
						Authenticating...
					</h2>
					<p style="color: var(--text-secondary);" class="text-sm">
						Please wait while we complete your sign-in
					</p>
				</div>
			</div>
		{:else if errorMessage}
			<div class="space-y-6">
				<!-- Error Icon -->
				<div class="flex justify-center">
					<div
						style="background: var(--bg-error); color: var(--text-error);"
						class="w-16 h-16 rounded-full flex items-center justify-center"
					>
						<i class="ri-error-warning-line text-2xl"></i>
					</div>
				</div>

				<div class="space-y-4">
					<h2 style="color: var(--text-primary);" class="text-xl font-semibold">
						Authentication Failed
					</h2>
					<p style="color: var(--text-error);" class="text-sm">
						{errorMessage}
					</p>
					<button
						onclick={() => goto('/auth/login')}
						style="background: var(--bg-button-primary); color: var(--text-button-primary);"
						class="w-full py-2.5 px-4 text-sm font-medium rounded-lg hover:bg-[var(--bg-button-hover-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--ring-primary)] transition-colors"
					>
						Try Again
					</button>
				</div>
			</div>
		{/if}
	</div>
</main>
