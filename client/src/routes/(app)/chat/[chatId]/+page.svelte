<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { marked } from 'marked';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { uploadedDocumentId } from '$lib/store/document';
	import DocumentViewer from '$lib/components/DocumentViewer.svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import type { Message, Conversation, MessageResponse } from '$lib/types/conversation';
	import { sendMessage, updateConversation } from '$lib/services/conversation';
	import {
		conversations,
		addConversation,
		addMessageToConversation,
		currentConversation
	} from '$lib/store/conversation';
	import { indexedDbService } from '$lib/services/indexedDb';

	let chatContainer: HTMLDivElement;

	let chatId = $state(page.params.chatId);
	let userInput = $state('');
	let documentId = $state<string | null>(null);
	let isTemp = $state(false);
	let query = $state<string | null>(null);
	let error = $state<boolean | null>(false);
	let firstMessage = false;

	let isSmallScreen = $state(false);
	let currentView: 'pdf' | 'chat' = $state('pdf');

	const conversation = $derived(chatId ? $conversations.get(chatId) : undefined);
	let messages: Message[] = $derived(conversation?.messages ?? []);

	const fetchUpdates = async (convId: string) => {
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

	$effect(() => {
		if (conversation?.documents?.[0]?.id) {
			documentId = conversation.documents[0].id as string;
		}
	});

	$effect(() => {
		chatId = page.params.chatId;
		if (chatId === 'new') {
			documentId = $uploadedDocumentId || '';
			isTemp = false; // Assuming uploaded documents go to 'document' store
			firstMessage = true;
			currentConversation.set(null);
		} else if (chatId && !firstMessage) {
			currentConversation.set(chatId);
			fetchUpdates(chatId);
		}
	});

	onMount(() => {
		const handleResize = () => {
			if (typeof window !== 'undefined') {
				isSmallScreen = window.innerWidth < 900;
			}
		};

		handleResize();
		window.addEventListener('resize', handleResize);

		return () => {
			window.removeEventListener('resize', handleResize);
		};
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
	async function handleSendMessage(text: string): Promise<Error | void> {
		query = text;
		error = false;
		userInput = '';

		scrollToBottom();
		try {
			const response: MessageResponse = await sendMessage(query, $currentConversation);

			if (!$currentConversation) {
				const conv: Conversation = {
					id: response.conversationId,
					title: query,
					messages: [response.userMessage, response.assistantMessage],
					documents: [{ id: response.fileId as string, title: '', createdAt: '' }],
					createdAt: response.createdAt as string,
					updatedAt: response.updatedAt as string
				};

				console.log('from handleSendMessage, conversation: ', conv);

				await indexedDbService.addRecord('conversation', conv);
				addConversation(conv);

				uploadedDocumentId.set(null);
				firstMessage = false;
				goto(`/chat/${response.conversationId}`, { replaceState: true });
				currentConversation.set(response.conversationId);
			} else {
				const conv: Conversation | undefined = addMessageToConversation(response.conversationId, [
					response.userMessage,
					response.assistantMessage
				]);

				if (!conv) return new Error('Conversation is not abailable locally');

				await indexedDbService.updateRecord('conversation', conv);
			}

			query = null;
		} catch {
			error = true;
		} finally {
			scrollToBottom();
			return;
		}
	}
	async function _sendMessage() {
		if (!query) {
			const trimmedInput = userInput.trim();
			if (!trimmedInput) return;
			await handleSendMessage(trimmedInput);
		}
	}
</script>

{#if isSmallScreen}
	<div
		class="fixed bottom-30 right-5 bg-[var(--bg-primary)] z-10 rounded-full overflow-hidden border-b border-[var(--border-primary)]"
	>
		<button
			class="w-10 h-10 flex items-center justify-center {currentView === 'pdf' ? 'hidden' : ''}"
			aria-label="switch pdf"
			onclick={() => (currentView = 'pdf')}
		>
			<i class="ri-file-text-fill"></i>
		</button>
		<button
			class="w-10 h-10 flex items-center justify-center {currentView === 'chat' ? 'hidden' : ''}"
			aria-label="switch chat"
			onclick={() => (currentView = 'chat')}
		>
			<i class="ri-chat-ai-fill"></i>
		</button>
	</div>
{/if}

<div class="flex h-full w-full text-[var(--text-primary)] font-sans">
	<!-- Left Side: PDF Viewer -->
	<div
		class="h-full p-2 md:p-5 {!isSmallScreen ? 'w-1/2' : 'w-full'} {isSmallScreen &&
		currentView !== 'pdf'
			? 'hidden'
			: ''}"
	>
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
	<div
		class="flex flex-1 flex-col h-full {!isSmallScreen ? 'w-1/2' : 'w-full'} {isSmallScreen &&
		currentView !== 'chat'
			? 'hidden'
			: ''}"
	>
		<!-- Chat Header -->
		<div class="min-h-16 items-center px-6 lg:flex hidden">
			<h4 class="text-lg font-medium">{conversation?.title}</h4>
		</div>

		<!-- Message Container -->
		<div
			bind:this={chatContainer}
			class="w-full flex-grow p-2 md:p-6 space-y-6 overflow-y-scroll overflow-x-hidden scroll-smooth"
		>
			{#each messages as message (message.id)}
				{#if message.role === 'assistant'}
					<div class="w-full pr-1 md:pr-5 flex items-start gap-3">
						<div
							class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-[var(--primary)] text-xl"
						>
							<i class="ri-gemini-fill"></i>
						</div>
						<div class="w-full rounded-xl rounded-tl-none text-base lg:leading-7">
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
			{#if query}
				<div class="flex items-start justify-end gap-3 mt-10">
					<div
						class="max-w-full rounded-xl rounded-tr-none bg-[var(--bg-secondary)] p-3 text-base text-[var(--text-primary)]"
					>
						<p>{query}</p>
					</div>
				</div>
				{#if error}
					<div class="w-full flex justify-start">
						<div
							class="flex h-7 w-7 mr-4 flex-shrink-0 items-center justify-center rounded-full text-[var(--primary)] text-xl"
						>
							<i class="ri-gemini-fill"></i>
						</div>
						<div class="flex items-center px-4 py-2 rounded-xl bg-[var(--bg-error)]">
							<span class="flex items-center text-red-500 text-sm"
								><i class="ri-error-warning-line text-xl mr-2"></i> Some error occur.</span
							>
							<button
								class="w-20 h-9 text-sm flex cursor-pointer items-center justify-center ml-5 bg-[var(--bg-primary)] rounded-full text-[var(--text-primary)] font-medium border border-[var(--border-secondary)]"
								onclick={_sendMessage}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="20"
									height="20"
									fill="currentColor"
									class="bi bi-arrow-clockwise mr-2"
									viewBox="0 0 16 16"
								>
									<path
										fill-rule="evenodd"
										d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"
									/>
									<path
										d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"
									/>
								</svg> Retry
							</button>
							<button
								class="w-9 h-9 rounded-full text-[var(--text-primary)] bg-[var(--bg-secondary)] ml-2 hidden"
								aria-label="edit message"
							>
								<i class="ri-pencil-line"></i>
							</button>
						</div>
					</div>
				{:else}
					<div class="w-full pr-5 flex items-start gap-3">
						<div
							class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-[var(--primary)] text-xl"
						>
							<i class="ri-gemini-fill"></i>
						</div>
						<div class="w-full rounded-xl rounded-tl-none text-base leading-7">
							<ul class="w-full space-y-1 animate-pulse">
								<li>
									<p
										class="w-4/5 h-6 block truncate rounded-lg bg-linear-to-r from-[var(--bg-primary)] to-[var(--bg-secondary)]"
									></p>
								</li>
								<li>
									<p
										class="w-3/5 h-6 mt-2 block truncate rounded-lg bg-linear-to-r from-[var(--bg-primary)] to-[var(--bg-secondary)]"
									></p>
								</li>
							</ul>
						</div>
					</div>
				{/if}
			{/if}
		</div>

		<!-- Input Form -->
		<div class=" bg-transparent p-4 pt-0">
			<div
				class="relative shadow-sm rounded-2xl overflow-hidden border border-[var(--border-primary)]"
				style="box-shadow:0 2px 8px -2px color(from var(--gradient-accent) srgb r
				g b/.16)"
			>
				<ChatInput _sendMesage={handleSendMessage} />
			</div>
		</div>
	</div>
</div>
