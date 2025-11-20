<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { marked } from 'marked';
	import { get } from 'svelte/store';
	import { page } from '$app/state';
	import { uploadedDocumentId } from '$lib/store/document';
	import DocumentViewer from '$lib/components/DocumentViewer.svelte';
	import type { Message, Conversation, MessageResponse } from '$lib/types/conversation';
	import { sendMessage, updateConversation } from '$lib/services/conversation';
	import {
		conversations,
		addConversation,
		addMessageToConversation,
		currentConversation
	} from '$lib/store/conversation';
	import { indexedDbService } from '$lib/services/indexedDb';

	let userInput = $state('');
	let chatContainer: HTMLDivElement;
	let documentId = $state<string | null>(null);
	let isTemp = $state(false);
	const chatId = page.params.chatId;

	if (chatId == 'new') {
		currentConversation.set(null);
	} else if (chatId) {
		currentConversation.set(chatId);
	}

	const conversation = $derived(chatId ? $conversations.get(chatId) : undefined);

	let messages: Message[] = $derived(conversation?.messages ?? []);

	onMount(() => {
		const convId = $currentConversation;
		if (!convId) return;

		const fetchUpdates = async () => {
			// Read from the store non-reactively using get() to prevent a dependency.
			const conversation = get(conversations).get(convId);
			let lastUpdated = new Date(0);

			if (conversation && conversation.messages.length > 0) {
				lastUpdated = conversation.messages.reduce((max, msg) => {
					const msgDate = new Date(msg.timeStamp);
					return msgDate > new Date(max) ? msgDate : max;
				}, lastUpdated);
			}
			await updateConversation(convId, lastUpdated.toISOString());
		};

		fetchUpdates();
	});

	$effect(() => {
		documentId = conversation?.documents[0].id as string;
	});

	$effect(() => {
		if (chatId === 'new') {
			documentId = $uploadedDocumentId || '';
			isTemp = false; // Assuming uploaded documents go to 'document' store
		}
	});

	async function scrollToBottom() {
		await tick();
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	/**
	 * Handles sending a user message.
	 * - Trims the user input.
	 * - Calls the sendMessage service to send the message to the backend.
	 * - Updates the conversation in the store and IndexedDB based on whether it's a new conversation or an existing one.
	 * - Scrolls the chat to the bottom after sending the message.
	 */
	async function handleSendMessage() {
		const trimmedInput = userInput.trim();
		if (!trimmedInput) return;

		userInput = '';
		const response: MessageResponse = await sendMessage(trimmedInput, $currentConversation);

		if (!$currentConversation) {
			const conv: Conversation = {
				id: response.conversationId,
				title: trimmedInput,
				messages: [response.userMessage, response.assistantMessage],
				documents: [response.fileId as string],
				createdAt: response.createdAt as string,
				updatedAt: response.updatedAt as string
			};

			await indexedDbService.addRecord('conversation', conv);
			addConversation(conv);

			uploadedDocumentId.set(null);
			page.params.chatId = response.conversationId;
		} else {
			const conv: Conversation | undefined = addMessageToConversation(response.conversationId, [
				response.userMessage,
				response.assistantMessage
			]);

			if (!conv) return new Error('Conversation is not abailable locally');

			await indexedDbService.updateRecord('conversation', conv);
		}

		scrollToBottom();
	}

	async function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			await handleSendMessage();
		}
	}
</script>

<div class="flex h-screen w-full text-[var(--text-primary)] font-sans">
	<!-- Left Side: PDF Viewer -->
	<div class="w-1/2 h-fulli p-5">
		{#if documentId}
			<div class="h-full w-full overflow-hidden rounded-xl">
				<DocumentViewer {documentId} {isTemp} />
			</div>
		{:else}
			<div class="flex h-full items-center justify-center text-[var(--text-muted)]">
				<p>No document to display</p>
			</div>
		{/if}
	</div>

	<!-- Right Side: Chat Interface -->
	<div class="w-1/2 flex flex-1 flex-col h-screen">
		<!-- Chat Header -->
		<header class="flex h-16 items-center px-6">
			<h1 class="text-lg font-semibold">Ask PDF</h1>
		</header>

		<!-- Message Container -->
		<div
			bind:this={chatContainer}
			class="w-full flex-grow p-6 space-y-6 overflow-y-scroll overflow-x-hidden"
		>
			{#each messages as message (message.id)}
				{#if message.role === 'assistant'}
					<div class="w-full pr-5 flex items-start gap-3">
						<div
							class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-[var(--primary)] text-xl"
						>
							<i class="ri-gemini-fill"></i>
						</div>
						<div class="w-full rounded-xl rounded-tl-none text-base leading-7">
							{@html marked.parse(message.text)}
						</div>
					</div>
				{:else}
					<div class="flex items-start justify-end gap-3 mt-10">
						<div
							class="max-w-full rounded-xl rounded-tr-none bg-[var(--bg-secondary)] p-3 text-base text-[var(--text-primary)]"
						>
							<p>{message.text}</p>
						</div>
					</div>
				{/if}
			{/each}
		</div>

		<!-- Input Form -->
		<div class=" bg-transparent p-4 pt-0">
			<div
				class="relative shadow-sm rounded-2xl overflow-hidden border border-[var(--border-primary)]"
				style="box-shadow:0 2px 8px -2px color(from var(--gradient-accent) srgb r
				g b/.16)"
			>
				<textarea
					bind:value={userInput}
					onkeydown={handleKeydown}
					rows="3"
					placeholder="Ask a question about the PDF..."
					class="w-full outline-none border-none resize-none bg-[var(--bg-primary)] p-3 pr-12 text-sm"
				></textarea>
				<button
					onclick={handleSendMessage}
					aria-label="Send message"
					class="absolute bottom-2.5 right-2.5 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary)] text-white hover:opacity-90 disabled:opacity-50"
					disabled={!userInput.trim()}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						height="50%"
						width="50%"
						class="ml-[2px]"
						viewBox="0 0 20 20"
						fill="currentColor"
						transform="rotate(90)"
					>
						<path
							d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"
						/>
					</svg>
				</button>
			</div>
		</div>
	</div>
</div>
