//# The client will:

// Connect to the specified server
// List available tools
// Start an interactive chat session where you can:
// Enter queries
// See tool executions
// Get responses from Claude

// # How It Works
// When you submit a query:

// The client gets the list of available tools from the server
// Your query is sent to Claude along with tool descriptions
// Claude decides which tools (if any) to use
// The client executes any requested tool calls through the server
// Results are sent back to Claude
// Claude provides a natural language response
// The response is displayed to you

//#1 STEP Basic Client Structure: create the basic client class in index.ts todo is index.ts right?

/**
 * MCPClient - API client to connect to our Python backend with MCP tool support
 * This service handles all communication with the AI backend server.
 */
export class MCPClient {
  private apiUrl: string;
  private isConnected: boolean = false;
  private tools: any[] = [];

  constructor() {
    // Get backend URL from environment or use default
    this.apiUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3002';
  }

  /**
   * Connect to the AI backend server
   * The serverScriptPath param is kept for compatibility but not used
   */
  async connectToServer(serverScriptPath: string): Promise<boolean> {
    try {
      // Check if the backend is running
      const healthResponse = await fetch(`${this.apiUrl}/api/health`);
      const healthData = await healthResponse.json();

      // If health check shows connected, we should explicitly get the tools
      if (healthData.connected) {
        this.isConnected = true;

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
          }
        } else {
          // Fallback to /api/tools if /api/connect fails
          await this.fetchTools();
        }

        return true;
      }

      // Otherwise try to initialize connection
      const response = await fetch(`${this.apiUrl}/api/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({}) // We don't need serverPath anymore
      });

      if (!response.ok) {
        throw new Error(`Failed to connect to AI service: ${response.statusText}`);
      }

      const data = await response.json();
      this.isConnected = data.status === 'connected';

      // Store available tools
      if (this.isConnected && data.tools) {
        this.tools = data.tools;
        console.log(`Connected with ${this.tools.length} tools available`);
      }

      return this.isConnected;
    } catch (error) {
      console.error('Error connecting to AI service:', error);
      this.isConnected = false;
      return false;
    }
  }

  /**
   * Process a user message through the AI
   */
  async processQuery(query: string): Promise<string> {
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
        throw new Error(`Failed to process query: ${response.statusText}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error processing query:', error);
      return `Error processing your request: ${(error as Error).message}`;
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

  /**
   * Send a message to the direct chat endpoint that uses raw receipt context
   *
   * @param message User message to send
   * @param model Optional Gemini model name to use
   * @returns Response from the direct chat endpoint
   */
  async sendDirectContextMessage(
    message: string,
    model: string = 'gemini-2.0-flash' //todo change to 2.5-pro
  ): Promise<string> {
    try {
      // Now using the main chat endpoint instead of direct_chat
      // Since receipt context is now built into the agent's system prompt
      const url = `${this.apiUrl}/api/chat`;

      // Send the request with message
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
      });

      // Check if the request was successful
      if (!response.ok) {
        throw new Error(`Chat request failed with status ${response.status}`);
      }

      // Parse the response
      const data = await response.json();
      let responseText = data.response;

      // Safety check: Filter out any tool command artifacts that might slip through
      if (typeof responseText === 'string') {
        if (
          responseText.includes('tool_code') ||
          responseText.includes('sequential_thinking.run') ||
          responseText.includes('memory_tool') ||
          responseText.includes('brave_search')
        ) {
          console.error('Tool command detected in response:', responseText);
          responseText =
            "I'm analyzing your information to provide insights. Please ask me a specific question about your finances or receipts.";
        }
      }

      return responseText;
    } catch (error) {
      console.error('Error sending direct chat message:', error);
      throw error;
    }
  }
}
