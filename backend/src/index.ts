import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { MCPService } from './services/mcpService';
import path from 'path';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const mcpService = new MCPService();

// Middleware
app.use(cors());
app.use(express.json());

// Initialize MCP Service
const serverScriptPath = process.env.MCP_SERVER_PATH;
if (!serverScriptPath) {
  console.warn('Warning: MCP_SERVER_PATH not set. Service will start disconnected.');
} else {
  // Connect to the MCP server when the application starts
  mcpService
    .connectToServer(serverScriptPath)
    .then((success) => {
      if (success) {
        console.log(`Successfully connected to MCP server at ${serverScriptPath}`);
      } else {
        console.error(`Failed to connect to MCP server at ${serverScriptPath}`);
      }
    })
    .catch((err) => {
      console.error('Error connecting to MCP server:', err);
    });
}

// API Routes/urls, need more comments
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', connected: mcpService.isServerConnected() });
});

app.get('/api/tools', (req, res) => {
  if (!mcpService.isServerConnected()) {
    return res.status(503).json({ error: 'MCP server not connected' });
  }
  res.json({ tools: mcpService.getTools() });
});

app.post('/api/connect', async (req, res) => {
  const { serverPath } = req.body;

  if (!serverPath) {
    return res.status(400).json({ error: 'Server path is required' });
  }

  try {
    const success = await mcpService.connectToServer(serverPath);
    if (success) {
      res.json({ status: 'connected', tools: mcpService.getTools() });
    } else {
      res.status(500).json({ error: 'Failed to connect to server' });
    }
  } catch (error) {
    res.status(500).json({ error: `Connection error: ${(error as Error).message}` });
  }
});

app.post('/api/chat', async (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  if (!mcpService.isServerConnected()) {
    return res.status(503).json({ error: 'MCP server not connected' });
  }

  try {
    const response = await mcpService.processQuery(message);
    res.json({ response });
  } catch (error) {
    res.status(500).json({ error: `Processing error: ${(error as Error).message}` });
  }
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`MCP Backend server running on port ${PORT}`);
});

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await mcpService.cleanup();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  await mcpService.cleanup();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
