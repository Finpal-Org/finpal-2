<script lang="ts">
  import './app.css';
  import Button from './lib/components/ui/button/button.svelte';
  import Home from './lib/HomePage.svelte';
  import Receipt from './lib/ReceiptPage.svelte';
  import Auth from './lib/AuthPage.svelte';
  import AiChat from './lib/AiChatPage.svelte';
  import ReportsPage from './lib/ReportsPage.svelte';
  import Analysis from './lib/AnalysisPage.svelte';
  import Navbar from './lib/components/Navbar.svelte';
  import Router from 'svelte-spa-router';
  import { ModeWatcher, toggleMode } from 'mode-watcher';
  import { onAuthStateChanged } from '../firebase/fireAuth';
  import { onMount } from 'svelte';
  import { push, location } from 'svelte-spa-router';

  // Authentication state
  let isAuthenticated = $state(false);
  let userLoading = $state(true);

  // Keep track of current location
  let currentPath = $derived($location);

  // Routes configuration - conditionally include routes based on auth state
  let routes = $derived({
    '/': isAuthenticated ? Receipt : Auth,
    '/receipts': isAuthenticated ? Receipt : Auth,
    '/aichat': isAuthenticated ? AiChat : Auth,
    '/analysis': isAuthenticated ? Analysis : Auth,
    '/reports': isAuthenticated ? ReportsPage : Auth,
    '/auth': Auth,
    '*': isAuthenticated ? Home : Auth
  });

  // Setup auth listener on mount
  onMount(() => {
    const unsubscribe = onAuthStateChanged((user) => {
      const wasAuthenticated = isAuthenticated;
      isAuthenticated = !!user;
      userLoading = false;

      // Handle auth state change navigations
      if (!wasAuthenticated && isAuthenticated) {
        // User just logged in
        if (currentPath === '/auth' || currentPath === '/') {
          push('/receipts');
        }
      } else if (wasAuthenticated && !isAuthenticated) {
        // User just logged out
        push('/auth');
      }
    });

    // Cleanup subscription on component destroy
    return unsubscribe;
  });
</script>

<main>
  <!-- start as dark theme -->
  <ModeWatcher />

  <div class="">
    {#if userLoading}
      <!-- Loading state -->
      <div class="flex h-screen items-center justify-center">
        <p class="text-lg">Loading...</p>
      </div>
    {:else}
      <!-- Show navbar when authenticated -->
      {#if isAuthenticated}
        <!-- TODO: make navbar resposive in < 640px into collapsable bar -->
        <Navbar />
      {/if}

      <!-- Main content -->
      <div class="mx-auto px-4 py-4">
        <!-- Routing -->
        <Router {routes} />
      </div>
    {/if}
  </div>
</main>

<style>
</style>
