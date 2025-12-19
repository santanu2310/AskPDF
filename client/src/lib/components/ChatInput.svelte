<script lang="ts">
	import { onMount } from 'svelte';

	interface Props {
		_sendMesage: (text: string) => Promise<Error | void>;
	}

	let { _sendMesage }: Props = $props();

	let editorNode: HTMLDivElement | undefined = $state();
	let chatWrapper: HTMLDivElement | undefined = $state();
	let sendBtn: HTMLButtonElement | undefined = $state();
	let measureNode: HTMLSpanElement | undefined = $state();

	let text = $state('');
	let wrapperWidth = $state(0);
	let textWidth = $state(0);
	let currentHeight = $state(0);

	// Update measurements whenever text or wrapperWidth changes
	$effect(() => {
		// Reference text to ensure reactivity
		const _ = text;
		if (measureNode) {
			textWidth = measureNode.offsetWidth;
		}
		if (editorNode) {
			currentHeight = editorNode.scrollHeight;
		}
	});

	let isLineOverflow = $derived.by(() => {
		if (!chatWrapper || wrapperWidth === 0) return false;

		const btnWidth = sendBtn ? sendBtn.offsetWidth : 40; // fallback approx
		const gap = 8;
		const inputPadding = 16; // 8px left + 8px right

		// wrapperWidth is contentRect width (excludes wrapper padding)
		const availableTextWidth = wrapperWidth - gap - btnWidth - inputPadding;

		// Add a small buffer/tolerance
		return textWidth > availableTextWidth - 5;
	});

	// Use scrollHeight to detect actual vertical expansion (newlines or wrapping)
	// 32px allows for ~24px line-height + padding
	let isMultiLine = $derived(currentHeight > 32 || isLineOverflow);

	onMount(() => {
		if (chatWrapper) {
			const ro = new ResizeObserver((entries) => {
				for (const entry of entries) {
					wrapperWidth = entry.contentRect.width;
				}
			});
			ro.observe(chatWrapper);
			return () => ro.disconnect();
		}
	});

	// Handle the keydown event
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault(); // Prevent standard new line
			sendMessage();
		}
	}

	async function sendMessage() {
		const trimmed = text.trim();
		if (trimmed.length == 0) return;
		text = '';
		await _sendMesage(trimmed);
	}

	// Optional: Handle paste to strip rich text formatting (keeping it plain text)
	function handlePaste(e: ClipboardEvent) {
		e.preventDefault();
		const plainText = e.clipboardData?.getData('text/plain') ?? '';
		document.execCommand('insertText', false, plainText);
	}
</script>

<div
	class="chat-wrapper flex items-end gap-2 p-3 relative shadow-sm rounded-2xl overflow-hidden border border-[var(--border-primary)]"
	style="box-shadow:0 2px 8px -2px color(from var(--gradient-accent) srgb r g b/.16)"
	class:multi-line={isMultiLine}
	bind:this={chatWrapper}
>
	<!-- 
    contenteditable="true" makes the div act like a textarea.
    bind:innerText syncs the content.
  -->
	<div
		class="input-area flex-1 w-full max-h-40 overflow-y-auto min-h-6 outline-none text-base py-1 px-2 whitespace-pre-wrap break-words"
		role="textbox"
		tabindex="0"
		aria-multiline="true"
		contenteditable="true"
		bind:this={editorNode}
		bind:innerText={text}
		onkeydown={handleKeydown}
		onpaste={handlePaste}
		data-placeholder="Ask any question about the PDF..."
	></div>

	<!-- Button stays at the bottom due to flex alignment -->
	<button
		class="bg-transparent flex items-center justify-center self-end pl-3 text-2xl border-l border-[var(--text-secondary)] text-[var(--text-secondary)]"
		onclick={sendMessage}
		aria-label="Send Message"
		bind:this={sendBtn}
	>
		<i class="ri-send-plane-2-fill" class:btn-enable={textWidth > 0}></i>
	</button>
</div>

<!-- Invisible element to measure text width -->
<span bind:this={measureNode} class="measure-ghost" aria-hidden="true">{text}</span>

<style>
	.chat-wrapper.multi-line {
		flex-direction: column;
		align-items: stretch;
		border-radius: 16px;
	}

	/* Placeholder trick using CSS */
	.input-area:empty::before {
		content: attr(data-placeholder);
		color: #888;
		pointer-events: none;
		display: block;
	}

	.multi-line {
		align-self: flex-end;
	}

	.btn-enable {
		color: var(--primary);
	}

	.measure-ghost {
		position: absolute;
		visibility: hidden;
		white-space: pre;
		font-size: 16px;
		font-family: inherit; /* Should match the input's font family */
		font-weight: normal; /* Match input */
		letter-spacing: normal;
		padding: 0;
		border: 0;
		left: -9999px;
		top: -9999px;
	}
</style>
