/**
 * MCPClient - API client to connect to our Python backend with MCP tool support
 * This service handles all communication with the AI backend server.
 */
export class MCPClient {
  private apiUrl: string;
  private remoteApiUrl?: string;
  private isConnected: boolean = false;
  private tools: any[] = [];

  constructor() {
    // Prioritize local backend over remote server
    this.apiUrl = 'http://localhost:3002';

    // Store remote URL as fallback if defined in environment
    if (import.meta.env.VITE_BACKEND_URL) {
      this.remoteApiUrl = import.meta.env.VITE_BACKEND_URL;
    }
  }

  /**
   * Connect to the AI backend server
   * The serverScriptPath param is kept for compatibility but not used
   */
  async connectToServer(serverScriptPath: string): Promise<boolean> {
    try {
      // First attempt to connect to local backend
      try {
        const healthResponse = await fetch(`${this.apiUrl}/api/health`);
        const healthData = await healthResponse.json();

        if (healthData.connected) {
          this.isConnected = true;
          console.log('Connected to local backend successfully');
          return await this.getServerTools();
        }
      } catch (localError) {
        console.log('Could not connect to local backend, trying remote...');
      }

      // If local failed and we have a remote URL, try that instead
      if (this.remoteApiUrl) {
        try {
          const remoteHealthResponse = await fetch(`${this.remoteApiUrl}/api/health`);
          const remoteHealthData = await remoteHealthResponse.json();

          if (remoteHealthData.connected) {
            // Switch to remote URL
            this.apiUrl = this.remoteApiUrl;
            this.isConnected = true;
            console.log('Connected to remote backend successfully');
            return await this.getServerTools();
          }
        } catch (remoteError) {
          console.error('Failed to connect to remote backend');
        }
      }

      // If we got here, both local and remote failed
      this.isConnected = false;
      return false;
    } catch (error) {
      console.error('Error connecting to backend:', error);
      this.isConnected = false;
      return false;
    }
  }

  // Helper method to get tools from the connected server
  private async getServerTools(): Promise<boolean> {
    try {
      // Always get a fresh list of tools via POST to /api/connect
      const connectResponse = await fetch(`${this.apiUrl}/api/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (connectResponse.ok) {
        const connectData = await connectResponse.json();
        if (connectData.tools) {
          this.tools = connectData.tools;
          console.log(`Connected with ${this.tools.length} tools available`);
          return true;
        }
      } else {
        // Fallback to /api/tools if /api/connect fails
        try {
          const toolsResponse = await fetch(`${this.apiUrl}/api/tools`);
          const toolsData = await toolsResponse.json();

          if (toolsData.tools) {
            this.tools = toolsData.tools;
            console.log(`Connected with ${this.tools.length} tools available via /api/tools`);
            return true;
          }
        } catch (toolsError) {
          console.error('Error fetching tools via fallback:', toolsError);
        }
      }

      return false;
    } catch (error) {
      console.error('Error getting tools:', error);
      return false;
    }
  }

  /**
   * Process a user message through the AI
   * Handles all types of messages, including those previously sent to direct_chat
   *
   * @param query User message to process
   * @returns AI response as string
   */
  async processMessage(query: string): Promise<string> {
    if (!this.isConnected) {
      return 'Error: Not connected to the AI service. Please try again later.';
    }

    try {
      const response = await fetch(`${this.apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: query })
      });

      if (!response.ok) {
        throw new Error(`Chat request failed with status ${response.status}`);
      }

      const data = await response.json();
      let responseText = data.response;

      // Parse the response to extract thinking vs actual content
      if (typeof responseText === 'string') {
        // If response already separates thinking and content with HTML, just return it
        if (
          responseText.includes('<div') &&
          (responseText.includes('tool_code') ||
            responseText.includes('sequential_thinking') ||
            responseText.includes('memory_tool') ||
            responseText.includes('brave_search'))
        ) {
          console.log('Response contains both thinking and content, preserving both');
          // The frontend will handle splitting these properly
          return responseText;
        }

        // If the response is pure tool commands with no HTML
        if (
          responseText.includes('tool_code') ||
          responseText.includes('sequential_thinking.think') ||
          responseText.includes('memory_tool') ||
          responseText.includes('brave_search')
        ) {
          console.log('Pure tool commands detected, preserving as thinking');

          // Create a synthetic response with both thinking and a generic content
          // The frontend will display the thinking in a collapsible bubble
          const htmlContent = `<div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-lg">I've analyzed your question and I'm ready to help. Check my thought process for details.</p>
          </div>`;

          // Return both parts - frontend will parse this
          return responseText + '\n\n' + htmlContent;
        }
      }

      // If we reach here, there are no tool commands, so return as is
      return responseText;
    } catch (error) {
      console.error('Error processing message:', error);
      return `Error processing your request: ${(error as Error).message}`;
    }
  }

  /**
   * Legacy method that now uses processMessage internally
   * @deprecated Use processMessage instead
   */
  async processQuery(query: string): Promise<string> {
    return this.processMessage(query);
  }

  /**
   * Legacy method that now uses processMessage internally
   * @deprecated Use processMessage instead
   */
  async sendDirectContextMessage(message: string): Promise<string> {
    return this.processMessage(message);
  }

  /**
   * Reset the conversation history on the backend
   * Call this when starting a new conversation or if token limit errors occur
   */
  async resetConversation(): Promise<{ status: string; message: string }> {
    try {
      const response = await fetch(`${this.apiUrl}/api/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Reset request failed with status ${response.status}`);
      }

      const data = await response.json();
      console.log('Conversation reset:', data.message);
      return data;
    } catch (error) {
      console.error('Error resetting conversation:', error);
      return {
        status: 'error',
        message: `Failed to reset conversation: ${(error as Error).message}`
      };
    }
  }

  /**
   * Fetch available tools from the backend
   */
  private async fetchTools(): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/api/tools`);
      if (response.ok) {
        const data = await response.json();
        this.tools = data.tools || [];
      }
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  }

  /**
   * Check if connected to the AI service
   */
  isServerConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Get list of available tools
   */
  getTools(): any[] {
    return this.tools;
  }
}
