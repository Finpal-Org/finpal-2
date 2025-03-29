# Backend MCP Service

This backend service provides a REST API for interacting with Model Context Protocol (MCP) servers. It allows you to connect to MCP servers, list available tools, and process queries using Claude or DeepSeek LLMs.

## Setup

1. Install dependencies:

   ```
   npm install
   ```

2. Create a `.env` file based on the `.env.example` file:

   ```
   cp .env.example .env
   ```

3. Update the `.env` file with your API keys and MCP server path:

   ```
   # API Keys for LLM
   ANTHROPIC_API_KEY=your-anthropic-api-key
   # Or DEEPSEEK_API_KEY=your-deepseek-api-key

   # MCP Server configuration
   MCP_SERVER_PATH=/path/to/your/mcp/server.js
   # or MCP_SERVER_PATH=/path/to/your/mcp/server.py

   # Server configuration
   PORT=3001
   ```

## Running the service

For development:

```
npm run dev
```

For production:

```
npm run build
npm start
```

## API Endpoints

### Health Check

```
GET /api/health
```

Returns the health status of the service and whether it's connected to an MCP server.

### Get Available Tools

```
GET /api/tools
```

Returns a list of available tools from the connected MCP server.

### Connect to MCP Server

```
POST /api/connect
```

Payload:

```json
{
  "serverPath": "/path/to/your/mcp/server.js"
}
```

Connects to the specified MCP server.

### Process Chat Message

```
POST /api/chat
```

Payload:

```json
{
  "message": "Your query here"
}
```

Processes a query using the LLM and any available tools from the MCP server.

##

    MCP Server Compatibility

This backend service works with any MCP-compatible server, including:

- Node.js servers
- Python servers

The server should implement the MCP protocol and provide one or more tools that the LLM can use.

## Error Handling

The service includes error handling for:

- Connection issues
- API request validation
- Tool execution errors
- LLM response processing
