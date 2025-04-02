<script lang="ts">
  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
  } from './components/ui/card';
  import { Button } from './components/ui/button';
  import { Input } from './components/ui/input';
  import { ScrollArea } from './components/ui/scroll-area';
  import { ArrowUp, Bot, User } from 'lucide-svelte';
  import { MCPClient } from './services/mcpService';
  import { onMount } from 'svelte';

  // Create our API client
  let apiClient: MCPClient; //the api variable
  let isConnected = false; // connection state

  // Initialize connection to the backend API
  async function initConnection() {
    try {
      // Create the client
      apiClient = new MCPClient();

      // Connect to backend (the parameter isn't used anymore but kept for compatibility)
      isConnected = await apiClient.connectToServer('');

      if (isConnected) {
        console.log('AI service connected successfully');
      } else {
        throw new Error('Failed to connect to AI service');
      }
    } catch (err) {
      console.log('AI connection Failed: ' + err);
      messages = [
        ...messages,
        {
          role: 'assistant',
          content:
            'Sorry, I failed to connect to the AI service. Please make sure the backend is running at http://localhost:3001'
        }
      ];
    }
  }

  // Initialize chat state with a welcome message
  let messages: Array<{ role: 'user' | 'assistant'; content: any }> = [
    {
      role: 'assistant',
      content: "Hello! I'm FinChat, your finance assistant. How can I help you today?"
    }
  ];

  // State variables for managing user input and loading state
  let userInput = '';
  let isLoading = false;

  // Send a message to the AI service
  async function handleSendMessage() {
    // Don't send empty messages
    if (!userInput.trim()) return;

    // Check if we're connected to the backend
    if (!isConnected) {
      messages = [
        ...messages,
        {
          role: 'assistant',
          content: 'Not connected to AI service. Please make sure the backend is running.'
        }
      ];
      return;
    }

    // Don't send if already waiting or if input is empty
    if (!userInput.trim() || isLoading) return;

    try {
      const messageToSend = userInput.trim();
      isLoading = true;

      // Add user message to the chat
      messages = [...messages, { role: 'user', content: messageToSend }];
      userInput = '';

      // Send to backend and get response
      const response = await apiClient.processQuery(messageToSend);

      // Add AI response to the chat
      messages = [...messages, { role: 'assistant', content: response }];
    } catch (error) {
      console.error('Error processing message:', error);
      messages = [
        ...messages,
        { role: 'assistant', content: 'Sorry, I encountered an error processing your request.' }
      ];
    } finally {
      isLoading = false;
    }
  }

  // Send message when Enter key is pressed (not Shift+Enter)
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  // Connect to the backend when the component loads
  onMount(() => {
    initConnection();
  });
</script>

<div class="container mx-auto flex h-[calc(100vh-2rem)] max-w-2xl flex-col px-4 py-8">
  <Card class="flex h-full flex-col border-0 shadow-lg">
    <CardHeader class="pb-2">
      <CardTitle class="flex items-center gap-2 text-xl">
        <Bot class="h-5 w-5 text-primary" />
        <span>FinPal Assistant</span>
      </CardTitle>
      <CardDescription>Your personal financial AI assistant</CardDescription>
    </CardHeader>

    <CardContent class="flex-grow overflow-hidden p-4">
      <ScrollArea class="h-full pr-4">
        <div class="flex flex-col gap-3">
          {#each messages as message}
            <div class={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                class={`flex max-w-[85%] gap-2 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div
                  class={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full 
                  ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
                >
                  {#if message.role === 'user'}
                    <User class="h-3.5 w-3.5" />
                  {:else}
                    <Bot class="h-3.5 w-3.5" />
                  {/if}
                </div>
                <div
                  class={`rounded-lg p-3 text-sm ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            </div>
          {/each}

          {#if isLoading}
            <div class="flex justify-start">
              <div class="flex max-w-[85%] gap-2">
                <div
                  class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-muted"
                >
                  <Bot class="h-3.5 w-3.5" />
                </div>
                <div class="rounded-lg bg-muted p-3">
                  <div class="flex gap-1">
                    <div class="h-1.5 w-1.5 animate-bounce rounded-full bg-current"></div>
                    <div
                      class="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
                      style="animation-delay: 150ms"
                    ></div>
                    <div
                      class="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
                      style="animation-delay: 300ms"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </ScrollArea>
    </CardContent>

    <CardFooter class="pt-2">
      <form class="flex w-full gap-2" on:submit|preventDefault={handleSendMessage}>
        <Input
          bind:value={userInput}
          placeholder="Type your message..."
          on:keydown={handleKeyDown}
          disabled={isLoading}
          class="flex-grow"
        />
        <Button
          type="submit"
          disabled={isLoading || !userInput.trim()}
          variant="default"
          size="icon"
          class="rounded-full"
        >
          <ArrowUp class="h-4 w-4" />
          <span class="sr-only">Send message</span>
        </Button>
      </form>
    </CardFooter>
  </Card>
</div>

<style></style>
