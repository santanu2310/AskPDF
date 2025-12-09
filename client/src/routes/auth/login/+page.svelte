<script lang="ts">
	import { scale } from 'svelte/transition';
	import icon from '$lib/assets/icon.png';
	import { guestRequest, AUTH_ENDPOINTS } from '$lib/services/api';

	let errorMessage = $state('');

	async function getAuthorizationUrl(provider: string) {
		try {
			const response = await guestRequest({
				method: 'get',
				url: AUTH_ENDPOINTS.OAUTH_URL(provider)
			});

			if (response.status != 200) {
				errorMessage = response.data.message || 'Authentication failed';
				return null;
			}
			return response.data.url;
		} catch (error) {
			errorMessage = 'Network error. Please try again.';
			return null;
		}
	}

	async function signInWithGitHub() {
		const authorizationUrl = await getAuthorizationUrl('github');
		window.location.href = authorizationUrl;
	}

	async function signInWithGoogle() {
		const authorizationUrl = await getAuthorizationUrl('google');
		window.location.href = authorizationUrl;
	}
</script>

<main
	style="background: var(--bg-primary); background-image: radial-gradient(ellipse 80% 80% at 50% -20%, var(--gradient-accent), var(--gradient-transparent));"
	class="relative flex flex-col items-center justify-center min-h-screen w-full transition-colors duration-300"
>
	<div
		style="background: var(--bg-secondary); border-color: var(--border-primary);"
		class="w-full max-w-md p-8 space-y-8 backdrop-blur-lg border rounded-2xl shadow-2xl"
	>
		<div class="text-center">
			<div class="mx-auto h-12 w-auto aspect-square">
				<img src={icon} alt="" />
			</div>
			<h2 style="color: var(--text-primary);" class="mt-6 text-3xl font-bold tracking-tight">
				Welcome
			</h2>
			<p style="color: var(--text-secondary);" class="mt-2 text-sm">
				Sign in to access your account
			</p>
		</div>

		<div class="space-y-4">
			<button
				onclick={signInWithGitHub}
				in:scale={{ start: 0.95, duration: 200, delay: 100 }}
				style="background: var(--bg-button-primary); color: var(--text-button-primary);"
				class="group w-full flex items-center justify-center p-2.5 text-sm font-semibold rounded-lg hover:bg-[var(--bg-button-hover-primary)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--ring-primary)] transition-transform transform-gpu hover:scale-[1.02] active:scale-[0.98]"
			>
				<i class="ri-github-fill text-lg mr-3"></i>
				Continue with GitHub
			</button>

			<button
				onclick={signInWithGoogle}
				in:scale={{ start: 0.95, duration: 200, delay: 200 }}
				style="background: var(--bg-button-secondary); color: var(--text-button-secondary); border-color: var(--border-secondary);"
				class="group w-full flex items-center justify-center p-3 text-sm font-semibold border rounded-lg hover:bg-[var(--bg-button-hover-secondary)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--ring-primary)] transition-transform transform-gpu hover:scale-[1.02] active:scale-[0.98]"
			>
				<svg
					class="w-5 h-5 mr-3"
					viewBox="0 0 48 48"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					aria-hidden="true"
				>
					<path
						fill="#FFC107"
						d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C12.955 4 4 12.955 4 24s8.955 20 20 20s20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"
					/>
					<path
						fill="#FF3D00"
						d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C16.318 4 9.656 8.337 6.306 14.691z"
					/>
					<path
						fill="#4CAF50"
						d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.222 0-9.618-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"
					/>
					<path
						fill="#1976D2"
						d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C42.099 34.551 44 29.829 44 24c0-1.341-.138-2.65-.389-3.917z"
					/>
				</svg>
				Continue with Google
			</button>
		</div>

		{#if errorMessage}
			<div
				role="alert"
				transition:scale={{ duration: 200 }}
				style="background: var(--bg-error); border-color: var(--border-error); color: var(--text-error);"
				class="mt-4 p-3 border text-sm rounded-lg text-center"
			>
				{errorMessage}
			</div>
		{/if}
	</div>
</main>
