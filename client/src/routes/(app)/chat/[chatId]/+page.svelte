<script>
  import { onMount, tick } from 'svelte';

  // --- Reactive State ---

  // Theme state. Defaults to false (light mode).
  let isDarkMode = false;
  
  // Holds the conversation messages.
  let messages = [
    { id: 1, sender: 'ai', text: 'Hello! Please upload a PDF, and I will be happy to answer your questions about it.' },
  ];

  // Binds to the user's input in the text area.
  let userInput = '';

  // A reference to the chat container for auto-scrolling.
  let chatContainer;


  /**
   * Scrolls the chat container to the bottom.
   */
  async function scrollToBottom() {
    // Wait for the DOM to update with the new message
    await tick(); 
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  /**
   * Handles sending a message, adding it to the chat, and simulating an AI response.
   */
  async function sendMessage() {
    const trimmedInput = userInput.trim();
    if (!trimmedInput) return;

    // Add user's message to the chat
    messages = [
      ...messages,
      { id: Date.now(), sender: 'user', text: trimmedInput }
    ];
    userInput = '';
    scrollToBottom();
    
    // Simulate AI thinking and responding
    setTimeout(() => {
      messages = [
        ...messages,
        { id: Date.now() + 1, sender: 'ai', text: 'Thinking... parsing your question.' }
      ];
      scrollToBottom();
    }, 1000);
  }

  /**
   * Handles the keydown event on the input to send a message on Enter press.
   */
  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

</script>

<div class:dark={isDarkMode} class="flex h-screen w-full bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans">
  <!-- Left Side: PDF Viewer Placeholder -->
  <div class="flex-1 border-r border-[var(--border-secondary)] bg-gray-50 dark:bg-gray-900/50">
    <!-- In a real application, a PDF viewer component would go here. -->
    <div class="flex h-full items-center justify-center text-[var(--text-muted)]">
      <p>PDF Viewer Area</p>
    </div>
  </div>

  <!-- Right Side: Chat Interface -->
  <div class="flex flex-1 flex-col h-screen">
    <!-- Chat Header -->
    <header class="flex h-16 items-center border-b border-[var(--border-secondary)] px-6">
      <h1 class="text-lg font-semibold">Ask PDF</h1>
    </header>

    <!-- Message Container -->
    <div bind:this={chatContainer} class="flex-grow overflow-y-auto p-6 space-y-6">
      {#each messages as message (message.id)}
        {#if message.sender === 'ai'}
          <!-- AI Message Bubble -->
          <div class="flex items-start gap-3">
            <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[var(--text-accent)] text-white">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.898 20.562L16.5 21.75l-.398-1.188a3.375 3.375 0 00-2.923-2.923L12 17.25l1.188-.398a3.375 3.375 0 002.923-2.923L16.5 12.75l.398 1.188a3.375 3.375 0 002.923 2.923L21 17.25l-1.188.398a3.375 3.375 0 00-2.923 2.923z" />
              </svg>
            </div>
            <div class="max-w-lg rounded-xl rounded-tl-none bg-[var(--bg-secondary)] p-3 text-sm">
              <p>{message.text}</p>
            </div>
          </div>
        {:else}
          <!-- User Message Bubble -->
          <div class="flex items-start justify-end gap-3">
             <div class="max-w-lg rounded-xl rounded-tr-none bg-[var(--text-accent)] p-3 text-sm text-white">
              <p>{message.text}</p>
            </div>
          </div>
        {/if}
      {/each}
    </div>

    <!-- Input Form -->
    <div class="border-t border-[var(--border-secondary)] bg-[var(--bg-secondary)]/50 p-4">
      <div class="relative">
        <textarea
          bind:value={userInput}
          on:keydown={handleKeydown}
          rows="1"
          placeholder="Ask a question about the PDF..."
          class="w-full resize-none rounded-lg border border-[var(--border-secondary)] bg-[var(--bg-primary)] p-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--ring-primary)]"
        ></textarea>
        <button
          on:click={sendMessage}
          aria-label="Send message"
          class="absolute bottom-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-[var(--text-accent)] text-white hover:opacity-90 disabled:opacity-50"
          disabled={!userInput.trim()}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
