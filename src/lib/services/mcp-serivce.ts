// //# The client will:

// // Connect to the specified server
// // List available tools
// // Start an interactive chat session where you can:
// // Enter queries
// // See tool executions
// // Get responses from Claude

// // # How It Works
// // When you submit a query:

// // The client gets the list of available tools from the server
// // Your query is sent to Claude along with tool descriptions
// // Claude decides which tools (if any) to use
// // The client executes any requested tool calls through the server
// // Results are sent back to Claude
// // Claude provides a natural language response
// // The response is displayed to you

// import { Anthropic } from '@anthropic-ai/sdk'; //deepseek-mcp-server

// import type { MessageParam, Tool } from '@anthropic-ai/sdk/resources/messages/messages.mjs'; //doc doesnt say its type
// import { Client } from '@modelcontextprotocol/sdk/client/index.js';
// import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
// import readline from 'readline/promises';

// //#1 STEP Basic Client Structure: create the basic client class in index.ts todo is index.ts right?

// //1. set the LLM key
// const DEEPSEEK_API_KEY = import.meta.env.VITE_DEEPSEEK_API_KEY; //import meta or process?
// if (!DEEPSEEK_API_KEY) {
//   throw new Error('DEEPSEEK_API_KEY is not set');
// }

// // Frontend MCP Client to interact with the backend API
// export class MCPClient {
//   private apiUrl: string;
//   private isConnected: boolean = false;
//   private tools: any[] = [];

//   constructor() {
//     this.apiUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';
//   }

//   /**
//    * Connect to the MCP server through the backend
//    * @param serverScriptPath Path to the MCP server script
//    */
//   async connectToServer(serverScriptPath: string): Promise<boolean> {
//     try {
//       // First check if backend is alive
//       const healthResponse = await fetch(`${this.apiUrl}/api/health`);
//       const healthData = await healthResponse.json();

//       // If already connected, just return true
//       if (healthData.connected) {
//         this.isConnected = true;
//         await this.fetchTools();
//         return true;
//       }

//       // Otherwise try to connect using the provided path
//       const response = await fetch(`${this.apiUrl}/api/connect`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ serverPath: serverScriptPath })
//       });

//       if (!response.ok) {
//         throw new Error(`Failed to connect to MCP server: ${response.statusText}`);
//       }

//       const data = await response.json();
//       this.isConnected = data.status === 'connected';

//       if (this.isConnected) {
//         this.tools = data.tools || [];
//       }

//       return this.isConnected;
//     } catch (error) {
//       console.error('Error connecting to MCP server:', error);
//       this.isConnected = false;
//       return false;
//     }
//   }

//   /**
//    * Process a query using the MCP server
//    * @param query The user's query to process
//    */
//   async processQuery(query: string): Promise<string> {
//     if (!this.isConnected) {
//       return 'Error: Not connected to the MCP service. Please try again later.';
//     }

//     try {
//       const response = await fetch(`${this.apiUrl}/api/chat`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ message: query })
//       });

//       if (!response.ok) {
//         throw new Error(`Failed to process query: ${response.statusText}`);
//       }

//       const data = await response.json();
//       return data.response;
//     } catch (error) {
//       console.error('Error processing query:', error);
//       return `Error processing your request: ${(error as Error).message}`;
//     }
//   }

//   /**
//    * Get the available tools from the MCP server
//    */
//   private async fetchTools(): Promise<void> {
//     try {
//       const response = await fetch(`${this.apiUrl}/api/tools`);
//       if (response.ok) {
//         const data = await response.json();
//         this.tools = data.tools || [];
//       }
//     } catch (error) {
//       console.error('Error fetching tools:', error);
//     }
//   }

//   /**
//    * Check if connected to the MCP server
//    */
//   isServerConnected(): boolean {
//     return this.isConnected;
//   }

//   /**
//    * Get available tools
//    */
//   getTools(): any[] {
//     return this.tools;
//   }
// }

// //todo Main Entry Point (remove not for web app)
// // async function main() {
// //   if (process.argv.length < 3) {
// //     console.log('Usage: node index.ts <path_to_server_script>');
// //     return;
// //   }
// //   const mcpClient = new MCPClient();
// //   try {
// //     await mcpClient.connectToServer(process.argv[2]);
// //     await mcpClient.chatLoop();
// //   } finally {
// //     await mcpClient.cleanup();
// //     process.exit(0);
// //   }
// // }

// // main();

// // todo Running client where?
// // # Build TypeScript
// // npm run build

// // # Run the client
// // node build/index.js path/to/server.py # python server
// // node build/index.js path/to/build/index.js # node server
