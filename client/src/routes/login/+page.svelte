<script>
  import { onMount } from 'svelte';
  import { scale } from 'svelte/transition';
  import icon from '$lib/assets/icon.png';

  // --- Reactive State ---

  // Theme state. Defaults to false (light mode).
  let isDarkMode = false;
  
  // Error message state. Set this to display a notification to the user.
  // Example: "OAuth provider is not configured. Please contact support."
  let errorMessage = '';

  // --- Lifecycle & Initialization ---

  onMount(() => {
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

    // --- Developer Note: Error message simulation ---
    // You can uncomment the line below to test the error message display.
    // In a real app, you would set this based on missing environment variables
    // or a failed API response.
    // errorMessage = "OAuth is not configured on this server.";
  });

  // --- Theme Management ---

  /**
   * Toggles the 'dark' class on the <html> element to apply Tailwind's dark mode styles.
   * @param {boolean} isDark - Whether to apply the dark theme.
   */
  function updateThemeClass(isDark) {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  /**
   * Toggles the theme between light and dark mode, updates the UI,
   * and persists the choice to localStorage.
   */
  function toggleTheme() {
    isDarkMode = !isDarkMode;
    updateThemeClass(isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }

  // --- OAuth Handlers ---

  /**
   * Redirects the user to the GitHub authentication endpoint on your server.
   */
  function signInWithGitHub() {
    console.log("Redirecting to GitHub OAuth endpoint...");
    // This should point to your backend route that initiates the GitHub OAuth flow.
    window.location.href = '/auth/github'; 
  }

  /**
   * Redirects the user to the Google authentication endpoint on your server.
   */
  function signInWithGoogle() {
    console.log("Redirecting to Google OAuth endpoint...");
    // This should point to your backend route that initiates the Google OAuth flow.
    window.location.href = '/auth/google';
  }

</script>

<div class:dark={isDarkMode}>
  <main class="relative flex flex-col items-center justify-center min-h-screen w-full bg-gray-100 dark:bg-gray-900 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] dark:bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] transition-colors duration-300">
    
    
    <!-- Glassmorphism Login Card -->
    <div class="w-full max-w-md p-8 space-y-8 bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg border border-white/20 dark:border-gray-700/50 rounded-2xl shadow-2xl">
      
      <!-- Header Section -->
      <div class="text-center">
        <!-- App Logo (Placeholder) -->
        <div class="mx-auto h-12 w-auto aspect-square">
          <img src={icon} alt="">
        </div>
        <h2 class="mt-6 text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
          Welcome Back
        </h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Sign in to access your account
        </p>
      </div>
      
      <!-- OAuth Buttons Container -->
      <div class="space-y-4">
        <!-- Continue with GitHub Button -->
        <button
          on:click={signInWithGitHub}
          in:scale={{ start: 0.95, duration: 200, delay: 100 }}
          class="group w-full flex items-center justify-center p-2.5 text-sm font-semibold text-white bg-gray-800 rounded-lg hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-800 dark:focus:ring-offset-gray-900 transition-transform transform-gpu hover:scale-[1.02] active:scale-[0.98]"
        >
          <i class="ri-github-fill text-lg mr-3"></i>
          Continue with GitHub
        </button>

        <!-- Continue with Google Button -->
        <button
          on:click={signInWithGoogle}
          in:scale={{ start: 0.95, duration: 200, delay: 200 }}
          class="group w-full flex items-center justify-center p-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-100 dark:focus:ring-offset-gray-900 transition-transform transform-gpu hover:scale-[1.02] active:scale-[0.98]"
        >
          <!-- Google Icon -->
          <svg class="w-5 h-5 mr-3" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C12.955 4 4 12.955 4 24s8.955 20 20 20s20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"/>
            <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C16.318 4 9.656 8.337 6.306 14.691z"/>
            <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.222 0-9.618-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"/>
            <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C42.099 34.551 44 29.829 44 24c0-1.341-.138-2.65-.389-3.917z"/>
          </svg>
          Continue with Google
        </button>
      </div>

      <!-- Error Message Area -->
      {#if errorMessage}
        <div 
          role="alert"
          transition:scale={{ duration: 200 }}
          class="mt-4 p-3 bg-red-100 dark:bg-red-900/50 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-200 text-sm rounded-lg text-center"
        >
          {errorMessage}
        </div>
      {/if}
      
    </div>
  </main>
</div>