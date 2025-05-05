<!-- Login/Signup screens  -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { signInWithGoogle, signInWithEmail, createUser } from '../../firebase/fireAuth';
  import Card from './components/ui/card/card.svelte';
  import CardHeader from './components/ui/card/card-header.svelte';
  import CardTitle from './components/ui/card/card-title.svelte';
  import CardDescription from './components/ui/card/card-description.svelte';
  import CardContent from './components/ui/card/card-content.svelte';
  import CardFooter from './components/ui/card/card-footer.svelte';
  import Button from './components/ui/button/button.svelte';
  import Input from './components/ui/input/input.svelte';
  import Label from './components/ui/label/label.svelte';
  import Separator from './components/ui/separator/separator.svelte';

  // Form states
  let isLogin = $state(true);
  let email = $state('');
  let password = $state('');
  let passwordConfirm = $state('');
  let displayName = $state('');
  let errorMessage = $state('');
  let isLoading = $state(false);

  // Toggle between login and signup
  function toggleForm() {
    isLogin = !isLogin;
    errorMessage = '';
  }

  // Sign in with Google
  async function handleGoogleSignIn() {
    isLoading = true;
    errorMessage = '';

    try {
      await signInWithGoogle();
      // Redirect will be handled by App.svelte auth state listener
    } catch (error: any) {
      errorMessage = error.message || 'Failed to sign in with Google';
      console.error('Google sign in error:', error);
    } finally {
      isLoading = false;
    }
  }

  // Email/Password sign in
  async function handleSubmit() {
    isLoading = true;
    errorMessage = '';

    try {
      if (!email || !password) {
        throw new Error('Please enter email and password');
      }

      // For signup, validate password match
      if (!isLogin) {
        if (password !== passwordConfirm) {
          throw new Error('Passwords do not match');
        }

        // Create account with display name
        await createUser(email, password, displayName);
      } else {
        // Login with email password
        await signInWithEmail(email, password);
      }

      // Redirect will be handled by App.svelte auth state listener
    } catch (error: any) {
      errorMessage = error.message || 'Authentication failed';
      console.error('Auth error:', error);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
  <Card class="w-full max-w-md shadow-lg">
    <CardHeader>
      <CardTitle class="text-center text-2xl">
        {isLogin ? 'Login' : 'Create Account'}
      </CardTitle>
      <CardDescription class="text-center">
        {isLogin
          ? 'Enter your credentials to access your account'
          : 'Fill in the form below to create your account'}
      </CardDescription>
    </CardHeader>

    <CardContent>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        {#if !isLogin}
          <!-- Display Name (Signup only) -->
          <div class="space-y-2">
            <Label for="displayName">Display Name</Label>
            <Input
              id="displayName"
              type="text"
              placeholder="Your name"
              bind:value={displayName}
              disabled={isLoading}
            />
          </div>
        {/if}

        <!-- Email -->
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="example@email.com"
            bind:value={email}
            disabled={isLoading}
            required
          />
        </div>

        <!-- Password -->
        <div class="space-y-2">
          <Label for="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            bind:value={password}
            disabled={isLoading}
            required
          />
        </div>

        {#if !isLogin}
          <!-- Confirm Password (Signup only) -->
          <div class="space-y-2">
            <Label for="passwordConfirm">Confirm Password</Label>
            <Input
              id="passwordConfirm"
              type="password"
              placeholder="••••••••"
              bind:value={passwordConfirm}
              disabled={isLoading}
              required
            />
          </div>
        {/if}

        {#if errorMessage}
          <p class="text-sm text-destructive">{errorMessage}</p>
        {/if}

        <!-- Submit Button -->
        <Button type="submit" class="w-full" disabled={isLoading}>
          {#if isLoading}
            Loading...
          {:else}
            {isLogin ? 'Sign In' : 'Create Account'}
          {/if}
        </Button>
      </form>

      <!-- Separator -->
      <div class="relative my-4">
        <Separator />
        <span
          class="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-xs text-muted-foreground"
          >OR</span
        >
      </div>

      <!-- Google Sign In -->
      <Button variant="outline" class="w-full" on:click={handleGoogleSignIn} disabled={isLoading}>
        <span class="flex items-center justify-center">
          <!-- Google Logo SVG TODO: change with just svg -->
          <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          Continue with Google
        </span>
      </Button>
    </CardContent>

    <CardFooter class="flex justify-center">
      <Button variant="link" on:click={toggleForm} disabled={isLoading}>
        {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Log In'}
      </Button>
    </CardFooter>
  </Card>
</div>
