<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.png';
	import { onMount } from 'svelte';
	import { user } from '$lib/store/user';
	import type { LayoutData } from './$types';

	let { data, children }: { data: LayoutData; children: any } = $props();

	$effect(() => {
		if ($user !== data.user && data.user) {
			user.set(data.user);
		}
	});
	onMount(() => {
		if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
			document.documentElement.classList.add('dark');
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-[var(--bg-primary)]">
	{@render children?.()}
</div>
