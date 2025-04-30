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
  let availableTools: Array<{ name: string }> = []; // Store the available tools for debugging
  let showDebugInfo = false; // Toggle for debug information

  // Initialize connection to the backend API
  async function initConnection() {
    try {
      // Create the client
      apiClient = new MCPClient();

      // Connect to backend (the parameter isn't used anymore but kept for compatibility)
      isConnected = await apiClient.connectToServer('');

      if (isConnected) {
        console.log('AI service connected successfully');
        // Get available tools for debugging
        availableTools = apiClient.getTools();
        console.log('Available tools:', availableTools);

        // Update welcome message when connected
        messages[0].content =
          "Hello! I'm FinChat, your finance assistant 💸. How can I help you today?";
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
            'Sorry, I failed to connect to the AI service. Please make sure the backend is running at http://localhost:3002'
        }
      ];
    }
  }

  // Initialize chat state with a welcome message
  let messages: Array<{ role: 'user' | 'assistant'; content: any; thinking?: string }> = [
    {
      role: 'assistant',
      content: 'Connecting to Backend.. will take a minute..'
    }
  ];

  // State variables for managing user input and loading state
  let userInput = '';
  let isLoading = false;
  let isThinking = false;

  // Simple function to initialize charts after content is added to DOM
  function enableCharts() {
    // Find all chart script tags and execute them
    setTimeout(() => {
      // Destroy any existing charts first to prevent "Canvas is already in use" errors
      try {
        // Check if Chart.js is available - need to use any type to avoid TypeScript errors
        const ChartJS = (window as any).Chart;
        if (ChartJS && document.getElementById('finpal-chart')) {
          const existingChart = ChartJS.getChart('finpal-chart');
          if (existingChart) {
            existingChart.destroy();
            console.log('Destroyed existing chart');
          }
        }
      } catch (e) {
        console.error('Error checking for existing charts:', e);
      }

      const chartScripts = document.querySelectorAll(
        'script[data-chart="true"]:not([data-executed="true"])'
      );
      chartScripts.forEach((script) => {
        try {
          // Mark script as executed to prevent multiple executions
          script.setAttribute('data-executed', 'true');
          // Safe execution using Function constructor instead of eval
          if (script.textContent) {
            console.log('About to execute script:', script.textContent); // Debug
            const executeScript = new Function(script.textContent);
            executeScript();
          }
        } catch (error) {
          console.error('Error executing chart script:', error);
          console.log('Problem script content:', script.textContent); // Debug
        }
      });
    }, 100);
  }

  // Simple HTML post-processor for chart data
  function processHtml(html: string): string {
    if (!html) return html;

    // For chart data, take a simpler approach
    if (html.includes('finpal-chart') && html.includes('<script>')) {
      // Simply remove the DOMContentLoaded event listener and keep the rest
      html = html.replace(
        /document\.addEventListener\(['"]DOMContentLoaded['"],\s*function\s*\(\)\s*\{/g,
        '// Direct initialization: '
      );

      // Also remove the closing part of the event listener
      html = html.replace(/\}\s*\)\s*;(?=\s*<\/script>)/g, '');

      // Add data-chart attribute to all scripts
      html = html.replace(/<script>/g, '<script data-chart="true">');

      console.log('Processed chart script');
    }

    return html;
  }

  // Filter to separate tool usage (thinking) from actual response
  function sanitizeResponse(response: string): { content: string; thinking?: string } {
    if (typeof response !== 'string') return { content: response };

    // Look for split between thinking and content (introduced by our backend changes)
    // The backend now puts a double newline between thinking and content
    const splitIndex = response.indexOf('\n\n<div');

    if (splitIndex !== -1) {
      // We found a clear split between thinking and content
      const thinking = response.substring(0, splitIndex).trim();
      let content = response.substring(splitIndex + 2).trim();

      // Process content for charts and unify backgrounds
      content = processHtml(content);
      content = unifyBackgrounds(content);

      return { content, thinking };
    }

    // Otherwise, check for HTML content
    const htmlStartIndex = response.indexOf('<div');

    if (htmlStartIndex > 0) {
      // There's text before the HTML - treat as thinking
      const thinking = response.substring(0, htmlStartIndex).trim();
      let content = response.substring(htmlStartIndex);

      content = processHtml(content);
      content = unifyBackgrounds(content);
      return { content, thinking };
    } else if (htmlStartIndex === 0) {
      // Response starts directly with HTML - no thinking to extract
      return { content: unifyBackgrounds(processHtml(response)) };
    }

    // Check for tool command patterns if no HTML is found
    const toolPatterns = [
      'tool_code',
      'sequential_thinking',
      'memory_tool',
      'brave_search',
      'google_maps',
      'yfinance'
    ];

    // If no HTML but contains tool commands, show a default message
    for (const pattern of toolPatterns) {
      if (response.includes(pattern)) {
        return {
          content:
            '<div class="p-4 bg-muted rounded-lg"><p class="text-lg">I\'ve analyzed your question. Please check my thought process for details.</p></div>',
          thinking: response
        };
      }
    }

    // Process content for charts even if no thinking was detected
    return { content: unifyBackgrounds(processHtml(response)) };
  }

  // Unify background colors to bg-muted
  function unifyBackgrounds(content: string): string {
    if (!content) return content;

    // Replace all color backgrounds with bg-muted
    content = content.replace(/bg-(blue|gray|purple|green|yellow)-50/g, 'bg-muted');
    content = content.replace(/bg-gray-100/g, 'bg-muted');

    return content;
  }

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
          content: 'Connecting to backend... Please give me a minute...'
        }
      ];
      return;
    }

    // Don't send if already waiting or if input is empty
    if (!userInput.trim() || isLoading) return;

    try {
      const messageToSend = userInput.trim();
      isLoading = true;
      isThinking = true;

      // Add user message to the chat
      messages = [...messages, { role: 'user', content: messageToSend }];
      userInput = '';

      // Send to direct context endpoint
      const response = await apiClient.sendDirectContextMessage(messageToSend);

      // Store raw response for debug purposes
      rawResponse = JSON.stringify(response, null, 2);

      // Check for token limit error
      if (
        typeof response === 'string' &&
        (response.includes('token count exceeds') ||
          response.includes('token limit') ||
          response.includes('exceeds the maximum number of tokens'))
      ) {
        console.error('Token limit exceeded. Resetting conversation...');

        // Add an error message for the user
        messages = [
          ...messages,
          {
            role: 'assistant',
            content:
              "I'm sorry, but I've hit a technical limit with the conversation size. Let me reset our chat to continue helping you."
          }
        ];

        // Reset the conversation on the backend
        const resetResult = await apiClient.resetConversation();
        console.log('Conversation reset result:', resetResult);

        // Tell the user what happened
        messages = [
          ...messages,
          {
            role: 'assistant',
            content:
              "I've reset our conversation. You can continue asking questions and I'll remember only this most recent context. What would you like to know?"
          }
        ];

        isThinking = false;
        isLoading = false;
        return;
      }

      // Separate thinking from actual response
      const { content, thinking } = sanitizeResponse(response);

      // Add AI response to the chat
      messages = [...messages, { role: 'assistant', content, thinking }];

      // Initialize any charts in the response
      enableCharts();

      isThinking = false;
    } catch (error) {
      console.error('Error processing message:', error);
      messages = [
        ...messages,
        { role: 'assistant', content: 'Sorry, I encountered an error processing your request.' }
      ];
      rawResponse = JSON.stringify(error, null, 2);
      isThinking = false;
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

  // Toggle debug information
  function toggleDebugInfo() {
    showDebugInfo = !showDebugInfo;
  }

  // For debug purposes
  let rawResponse = '';

  // Connect to the backend when the component loads
  onMount(() => {
    initConnection();
  });
</script>

<svelte:head>
  <!-- Load Chart.js for visualizations -->
  <script src="/scripts/chart.min.js"></script>
</svelte:head>

<div class="container mx-auto flex h-[calc(100vh-2rem)] max-w-2xl flex-col px-4 py-8">
  <Card class="flex h-full flex-col border-0 shadow-lg">
    <CardHeader class="pb-2">
      <CardTitle class="flex items-center gap-2 text-xl">
        <Bot class="h-5 w-5 text-primary" />
        <span>FinPal Assistant</span>
      </CardTitle>
      <CardDescription>Your personal financial AI assistant</CardDescription>

      <!-- Debug toggle button -->
      <div class="mt-2 flex items-center justify-end">
        <button
          on:click={toggleDebugInfo}
          class="text-xs text-gray-400 underline hover:text-gray-200"
        >
          {showDebugInfo ? 'Hide Debug Info' : 'Show Debug Info'}
        </button>
      </div>

      <!-- Debug info for MCP tools -->
      {#if showDebugInfo}
        <div class="mt-2 rounded-md bg-muted p-2 text-xs text-gray-200">
          <div>Connection status: {isConnected ? 'Connected' : 'Disconnected'}</div>
          <div>Available tools: {availableTools.length}</div>
          {#if availableTools.length > 0}
            <details>
              <summary class="cursor-pointer">Show tools</summary>
              <ul class="ml-4 list-disc">
                {#each availableTools as tool}
                  <li>{tool.name}</li>
                {/each}
              </ul>
            </details>
          {/if}

          {#if rawResponse}
            <details>
              <summary class="mt-2 cursor-pointer">Last Raw Response</summary>
              <pre
                class="mt-1 max-h-40 overflow-auto rounded bg-muted/60 p-2 text-xs">{rawResponse}</pre>
            </details>
          {/if}

          <!-- Message history debug -->
          <details>
            <summary class="mt-2 cursor-pointer">Message History</summary>
            <pre
              class="mt-1 max-h-40 overflow-auto rounded bg-muted/60 p-2 text-xs">{JSON.stringify(
                messages,
                null,
                2
              )}</pre>
          </details>
        </div>
      {/if}
    </CardHeader>

    <CardContent class="flex-grow overflow-hidden p-4">
      <ScrollArea class="h-full pr-4">
        <div class="flex flex-col gap-3">
          {#each messages as message, messageIndex (messageIndex)}
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
                <div class="flex flex-col gap-2">
                  <!-- Show thinking bubble if available -->
                  {#if message.role === 'assistant' && message.thinking}
                    <div
                      class="rounded-lg border-l-4 border-green-400 bg-muted p-3 text-xs text-gray-600"
                    >
                      <details>
                        <summary class="flex cursor-pointer items-center gap-1 font-medium">
                          <span class="text-green-600">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="16"
                              height="16"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              ><path d="M12 2a10 10 0 1 0 10 10H12V2Z" /><path
                                d="M21.17 8H12V2.83c2.72.45 5.29 2 7.17 4.17Z"
                              /></svg
                            >
                          </span>
                          <span>View AI thought process</span>
                        </summary>
                        <pre
                          class="mt-2 max-h-60 overflow-auto whitespace-pre-wrap rounded bg-gray-200 p-2 text-xs">{message.thinking}</pre>
                      </details>
                    </div>
                  {/if}

                  <!-- Main message content -->
                  <div
                    class={`rounded-lg p-3 text-sm ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-foreground'
                    }`}
                  >
                    {@html message.content}
                  </div>
                </div>
              </div>
            </div>
          {/each}

          {#if isLoading && isThinking}
            <div class="flex justify-start">
              <div class="flex max-w-[85%] gap-2">
                <div
                  class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-muted"
                >
                  <Bot class="h-3.5 w-3.5" />
                </div>
                <div
                  class="rounded-lg border-l-4 border-green-400 bg-gray-200 p-3 text-xs text-gray-600"
                >
                  <div class="flex items-center gap-2">
                    <span>AI thinking...</span>
                    <div class="flex gap-1">
                      <div class="h-1.5 w-1.5 animate-bounce rounded-full bg-green-500"></div>
                      <div
                        class="h-1.5 w-1.5 animate-bounce rounded-full bg-green-500"
                        style="animation-delay: 150ms"
                      ></div>
                      <div
                        class="h-1.5 w-1.5 animate-bounce rounded-full bg-green-500"
                        style="animation-delay: 300ms"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if isLoading && !isThinking}
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

<style>
  :global(#finpal-chart) {
    width: 100% !important;
    height: 300px !important;
  }

  :global(canvas[id^='finpal-chart']) {
    width: 100% !important;
    height: 300px !important;
  }
</style>
