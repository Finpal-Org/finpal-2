<script lang="ts">
  import { onMount } from 'svelte';
  import { signOut, onAuthStateChanged } from '../../../firebase/fireAuth';
  import Button from './ui/button/button.svelte';
  import { push } from 'svelte-spa-router';
  import { toggleMode } from 'mode-watcher';
  import * as Sheet from './ui/sheet/index';

  // User display name
  let displayName = '';

  // Update display name when AUTH state changes
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
      // App.svelte will handle navigation
    } catch (error: any) {
      console.error('Sign out error:', error);
    }
  }
</script>

<!-- Mobile Navbar -->
<div class="my-1 lg:hidden">
  <Sheet.Root>
    <Sheet.SheetTrigger>
      <Button variant="ghost" size="icon">
        <!-- hamburger icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="36"
          height="36"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          ><line x1="4" x2="20" y1="12" y2="12" /><line x1="4" x2="20" y1="6" y2="6" /><line
            x1="4"
            x2="20"
            y1="18"
            y2="18"
          /></svg
        >
      </Button>
    </Sheet.SheetTrigger>
    <Sheet.Content side="left">
      <Sheet.Header><Sheet.SheetTitle class="text-2xl">FinPal</Sheet.SheetTitle></Sheet.Header>

      <div class="children:font-lg my-2 flex flex-col gap-10">
        <!-- <a href="/#/" class=" text-lg font-medium transition-colors hover:text-primary">
          Dashboard
        </a> -->
        <a href="/#/receipts" class="text-lg font-medium transition-colors hover:text-primary">
          Receipts
        </a>
        <a href="/#/aichat" class="text-lg font-medium transition-colors hover:text-primary">
          AI Chat
        </a>
        <a href="/#/analysis" class="text-lg font-medium transition-colors hover:text-primary">
          Analysis
        </a>
        <a href="/#/reports" class="text-lg font-medium transition-colors hover:text-primary">
          Reports
        </a>
        <a href="/#/receipts" class="text-lg font-medium transition-colors hover:text-primary">
          Settings
        </a>
        <Button variant="link" size="icon" on:click={toggleMode}
          ><svg
            version="1.1"
            id="Layer_1"
            xmlns="http://www.w3.org/2000/svg"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            x="0px"
            y="0px"
            viewBox="0 0 122.88 122.89"
            style="enable-background:new 0 0 122.88 122.89"
            xml:space="preserve"
            ><g
              ><path
                d="M49.06,1.27c2.17-0.45,4.34-0.77,6.48-0.98c2.2-0.21,4.38-0.31,6.53-0.29c1.21,0.01,2.18,1,2.17,2.21 c-0.01,0.93-0.6,1.72-1.42,2.03c-9.15,3.6-16.47,10.31-20.96,18.62c-4.42,8.17-6.1,17.88-4.09,27.68l0.01,0.07 c2.29,11.06,8.83,20.15,17.58,25.91c8.74,5.76,19.67,8.18,30.73,5.92l0.07-0.01c7.96-1.65,14.89-5.49,20.3-10.78 c5.6-5.47,9.56-12.48,11.33-20.16c0.27-1.18,1.45-1.91,2.62-1.64c0.89,0.21,1.53,0.93,1.67,1.78c2.64,16.2-1.35,32.07-10.06,44.71 c-8.67,12.58-22.03,21.97-38.18,25.29c-16.62,3.42-33.05-0.22-46.18-8.86C14.52,104.1,4.69,90.45,1.27,73.83 C-2.07,57.6,1.32,41.55,9.53,28.58C17.78,15.57,30.88,5.64,46.91,1.75c0.31-0.08,0.67-0.16,1.06-0.25l0.01,0l0,0L49.06,1.27 L49.06,1.27z"
              /></g
            ></svg
          ></Button
        >
      </div>
    </Sheet.Content>
  </Sheet.Root>
</div>
<!-- Desktop Navbar -->
<!-- TODO make justify between Finapl - Signin -->
<div class="border-b">
  <div class="container mx-auto hidden h-16 items-center px-4 lg:flex">
    <!-- Logo/App Name -->
    <div class="mr-4 text-xl font-bold">FinPal</div>

    <!-- Nav Links -->
    <nav class="mx-auto hidden items-center justify-evenly gap-8 px-6 lg:flex">
      <!-- <a href="/#/" class="text-sm font-medium transition-colors hover:text-primary"> Dashboard </a> -->
      <a href="/#/receipts" class="text-sm font-medium transition-colors hover:text-primary">
        Receipts
      </a>
      <a href="/#/aichat" class="text-sm font-medium transition-colors hover:text-primary">
        AI Chat
      </a>
      <a href="/#/analysis" class="text-sm font-medium transition-colors hover:text-primary">
        Analysis
      </a>
      <a href="/#/reports" class="text-sm font-medium transition-colors hover:text-primary">
        Reports
      </a>
      <a href="/#/receipts" class="text-sm font-medium transition-colors hover:text-primary">
        Settings
      </a>
    </nav>

    <div class="ml-auto flex items-center space-x-4">
      <!-- User Info -->
      <div class="text-sm">Welcome, {displayName}</div>
      <!-- Sign Out Button -->
      <Button variant="outline" size="sm" on:click={handleSignOut}>Sign Out</Button>
      <!-- Dark mode button -->
      <Button variant="link" size="icon" on:click={toggleMode}
        ><svg
          version="1.1"
          id="Layer_1"
          xmlns="http://www.w3.org/2000/svg"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          x="0px"
          y="0px"
          viewBox="0 0 122.88 122.89"
          style="enable-background:new 0 0 122.88 122.89"
          xml:space="preserve"
          ><g
            ><path
              d="M49.06,1.27c2.17-0.45,4.34-0.77,6.48-0.98c2.2-0.21,4.38-0.31,6.53-0.29c1.21,0.01,2.18,1,2.17,2.21 c-0.01,0.93-0.6,1.72-1.42,2.03c-9.15,3.6-16.47,10.31-20.96,18.62c-4.42,8.17-6.1,17.88-4.09,27.68l0.01,0.07 c2.29,11.06,8.83,20.15,17.58,25.91c8.74,5.76,19.67,8.18,30.73,5.92l0.07-0.01c7.96-1.65,14.89-5.49,20.3-10.78 c5.6-5.47,9.56-12.48,11.33-20.16c0.27-1.18,1.45-1.91,2.62-1.64c0.89,0.21,1.53,0.93,1.67,1.78c2.64,16.2-1.35,32.07-10.06,44.71 c-8.67,12.58-22.03,21.97-38.18,25.29c-16.62,3.42-33.05-0.22-46.18-8.86C14.52,104.1,4.69,90.45,1.27,73.83 C-2.07,57.6,1.32,41.55,9.53,28.58C17.78,15.57,30.88,5.64,46.91,1.75c0.31-0.08,0.67-0.16,1.06-0.25l0.01,0l0,0L49.06,1.27 L49.06,1.27z"
            /></g
          ></svg
        ></Button
      >
    </div>
  </div>
</div>
