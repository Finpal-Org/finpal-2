// TOMMOROW PLANS: ADD AS MUCH TOOLS AS WE CAN, BRAVE,GOOGLE MAP..
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import dotenv from 'dotenv';

dotenv.config();

const API_KEY = process.env.DEEPSEEK_API_KEY;
if (!API_KEY) {
  throw new Error('DEEPSEEK_API_KEY is not set');
}

// Define types to avoid TypeScript errors
type Tool = any;

export class MCPService {
  private mcp: Client;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];
  private isConnected: boolean = false;

  constructor() {
    this.mcp = new Client(
      { name: 'mcp-service', version: '1.0.0' },
      {
        capabilities: {
          prompts: {},
          resources: {},
          tools: {}
        }
      }
    );
  }

  //todo add new tools
  private setupCustomTools() {}

  // TO CHANGE LLM CHANGE THE SCRIPT PATH AND KEY IN ENV
  async connectToServer(serverScriptPath: string): Promise<boolean> {
    try {
      const isJs = serverScriptPath.endsWith('.js');
      const isPy = serverScriptPath.endsWith('.py');
      if (!isJs && !isPy) {
        throw new Error('Server script must be a .js or .py file');
      }
      const command = isPy
        ? process.platform === 'win32'
          ? 'python'
          : 'python3'
        : process.execPath;

      this.transport = new StdioClientTransport({
        command,
        args: [serverScriptPath]
      });
      await this.mcp.connect(this.transport);

      const toolsResult = await this.mcp.listTools();
      this.tools = toolsResult.tools.map((tool) => {
        return {
          name: tool.name,
          description: tool.description,
          input_schema: tool.inputSchema
        };
      });

      console.log(
        'Connected to server with tools:',
        this.tools.map(({ name }) => name)
      );

      this.isConnected = true;
      return true;
    } catch (e) {
      console.error('Failed to connect to MCP server: ', e);
      this.isConnected = false;
      return false;
    }
  }

  async processQuery(query: string): Promise<string> {
    if (!this.isConnected) {
      return 'Error: Not connected to an MCP server';
    }

    try {
      // Log available tools for debugging
      console.log(
        'Available tools:',
        this.tools.map((t) => t.name)
      );

      // Find an appropriate tool
      // DeepSeek MCP might use different tool names like 'generate', 'complete', 'chat'
      const availableTools = this.tools.map((t) => t.name);

      // Choose the first available tool from our preferred list
      const preferredTools = ['generate', 'complete', 'chat', 'text'];
      const toolToUse = preferredTools.find((t) => availableTools.includes(t)) || availableTools[0];

      if (!toolToUse) {
        return 'No suitable tools available on the MCP server';
      }

      console.log(`Using tool: ${toolToUse}`);

      // Call the tool with the query - adapt arguments based on the tool name
      const result = await this.mcp.callTool({
        name: toolToUse,
        arguments: {
          // Different tools might expect different parameter names
          prompt: query,
          text: query,
          input: query,
          message: query
        }
      });

      // Handle different response formats
      if (result.content && Array.isArray(result.content)) {
        return result.content
          .filter((item) => item.type === 'text')
          .map((item) => item.text)
          .join('\n');
      }

      // If we didn't get a properly formatted content array
      return typeof result === 'object' ? JSON.stringify(result) : 'No response from the model';
    } catch (error) {
      console.error('Error processing query:', error);

      // Try each tool one by one as a fallback (#verbose but super safe)
      try {
        for (const tool of this.tools) {
          console.log(`Trying tool: ${tool.name}`);
          try {
            const result = await this.mcp.callTool({
              name: tool.name,
              arguments: {
                prompt: query,
                text: query,
                input: query,
                message: query
              }
            });

            // If we got a result, process it
            if (result) {
              if (result.content && Array.isArray(result.content)) {
                return result.content
                  .filter((item) => item.type === 'text')
                  .map((item) => item.text)
                  .join('\n');
              }

              return typeof result === 'object' ? JSON.stringify(result) : String(result);
            }
          } catch (e) {
            console.log(`Tool ${tool.name} failed, trying next...`);
          }
        }
      } catch (fallbackError) {
        console.error('All tools failed:', fallbackError);
      }

      return `Error processing query: ${(error as Error).message}`;
    }
  }

  getTools(): Tool[] {
    return this.tools;
  }

  isServerConnected(): boolean {
    return this.isConnected;
  }

  async cleanup(): Promise<void> {
    await this.mcp.close();
  }
}
