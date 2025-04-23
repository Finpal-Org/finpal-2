// Load environment variables
require('dotenv').config();

module.exports = {
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": [
        "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
        "/Users/unrankedalzahrani/Desktop/finpal-svelte"
      ]
    },
    "brave-search": {
      "command": "node",
      "args": [
        "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-brave-search/dist/index.js"
      ],
      "env": {
        "BRAVE_API_KEY": process.env.BRAVE_API_KEY
      }
    },
    "google-maps": {
      "command": "node",
      "args": [
        "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-google-maps/dist/index.js"
      ],
      "env": {
        "_comment": "This Google Maps API key is working correctly",
        "GOOGLE_MAPS_API_KEY": process.env.GOOGLE_MAPS_API_KEY || "AIzaSyB2kxDjle7yKIVJjoNVKw5vMkENy9TljQQ"
      }
    },
    "sequential-thinking": {
      "command": "node",
      "args": [
        "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
      ]
    },
    "yfinance": {
      "command": "npx",
      "args": ["-y", "@elektrothing/server-yahoofinance"]
    },
    "memory-bank": {
      "command": "npx",
      "args": ["-y", "@allpepper/memory-bank-mcp"],
      "env": {
        "MEMORY_BANK_ROOT": "/Users/unrankedalzahrani/Desktop/finpal-svelte/memory-bank"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}; 