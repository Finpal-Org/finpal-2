<script lang="ts">
  import "./app.css";
  import Button from "./lib/components/ui/button/button.svelte";
  import Home from "./lib/Home.svelte";
  import Receipt from "./lib/Receipt.svelte";
  import Auth from "./lib/Auth.svelte";
  import Navbar from "./lib/components/Navbar.svelte";
  import Router from "svelte-spa-router";
  import { ModeWatcher, toggleMode} from "mode-watcher";
  import { onAuthStateChanged } from "../firebase/fireAuth";
  import { onMount } from "svelte";

  // Authentication state
  let isAuthenticated = false;
  let userLoading = true;

  // Setup auth listener on mount
  onMount(() => {
    const unsubscribe = onAuthStateChanged((user) => {
      isAuthenticated = !!user;
      userLoading = false;
    });

    // Cleanup subscription on component destroy
    return unsubscribe;
  });

  // Routes configuration - conditionally include routes based on auth state
  $: routes = {
    "/": isAuthenticated ? Home : Auth,
    "/receipts": isAuthenticated ? Receipt : Auth,
    "/auth": Auth,
    "*": isAuthenticated ? Home : Auth,
  }
</script>

<main>
<!-- start as dark theme -->
<ModeWatcher/> 

  <div class="m-2">
  {#if userLoading}
    <!-- Loading state -->
    <div class="flex justify-center items-center h-screen">
      <p class="text-lg">Loading...</p>
    </div>
  {:else}
    <!-- Show navbar when authenticated -->
    {#if isAuthenticated}
      <Navbar />
    {/if}

    <!-- Main content -->
    <div class="container mx-auto px-4 py-4">
      {#if isAuthenticated}
        <!-- Additional authenticated-only content can go here -->
      {/if}

      <!-- Routing -->
      <Router {routes}/>
    </div>
  {/if}
</main>

<style>
</style>
