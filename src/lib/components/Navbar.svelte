<script lang="ts">
  import { onMount } from 'svelte';
  import { signOut, onAuthStateChanged } from '../../../firebase/fireAuth';
  import Button from './ui/button/button.svelte';
  import { push } from 'svelte-spa-router';
  import { toggleMode } from 'mode-watcher';

  // User display name
  let displayName = '';
  
  // Update display name when auth state changes
  onMount(() => {
    const unsubscribe = onAuthStateChanged((user) => {
      displayName = user?.displayName || user?.email?.split('@')[0] || 'User';
    });
    
    // Clean up subscription on component destruction
    return unsubscribe;
  });

  // Handle sign out
  async function handleSignOut() {
    try {
      await signOut();
      // Redirect will happen via App.svelte based on auth state
    } catch (error: any) {
      console.error('Sign out error:', error);
    }
  }
</script>

<div class="border-b">
  <div class="flex h-16 items-center px-4 container mx-auto">
    <!-- Logo/App Name -->
    <div class="mr-4 font-bold text-xl">FinPal</div>
    
    <!-- Nav Links -->
    <nav class="mx-6 flex items-center space-x-4 lg:space-x-6 hidden md:block">
      <a 
        href="/#/" 
        class="text-sm font-medium transition-colors hover:text-primary"
      >
        Dashboard
      </a>
      <a 
        href="/#/receipts" 
        class="text-sm font-medium transition-colors hover:text-primary"
      >
        Receipts
      </a>
    </nav>

    <div class="ml-auto flex items-center space-x-4">
      <!-- User Info -->
      <div class="text-sm">Welcome, {displayName}</div>
      
      <!-- Sign Out Button -->
      <Button variant="outline" size="sm" on:click={handleSignOut}>
        Sign Out
      </Button>
      <Button variant="outline" on:click={toggleMode}>Toggle Theme</Button>
    </div>
  </div>
</div> 