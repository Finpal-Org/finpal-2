// // Load environment variables if needed
// require('dotenv').config();

// // Export the configuration
// module.exports = {
//   mcpServers: {
//     "filesystem": {
//       "command": "node",
//       "args": [
//         process.env.NODE_MODULES_PATH || "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
//         process.env.PROJECT_PATH || "/Users/unrankedalzahrani/Desktop/finpal-svelte"
//       ]
//     },
//     "brave-search": {
//       "command": "node",
//       "args": [
//         process.env.NODE_MODULES_PATH ? `${process.env.NODE_MODULES_PATH}/@modelcontextprotocol/server-brave-search/dist/index.js` : "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-brave-search/dist/index.js"
//       ],
//       "env": {
//         "BRAVE_API_KEY": process.env.BRAVE_API_KEY
//       }
//     },
//     "google-maps": {
//       "command": "node",
//       "args": [
//         process.env.NODE_MODULES_PATH ? `${process.env.NODE_MODULES_PATH}/@modelcontextprotocol/server-google-maps/dist/index.js` : "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-google-maps/dist/index.js"
//       ],
//       "env": {
//         "_comment": "Google Maps API key",
//         "GOOGLE_MAPS_API_KEY": process.env.GOOGLE_MAPS_API_KEY
//       }
//     },
//     "sequential-thinking": {
//       "command": "node",
//       "args": [
//         process.env.NODE_MODULES_PATH ? `${process.env.NODE_MODULES_PATH}/@modelcontextprotocol/server-sequential-thinking/dist/index.js` : "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
//       ]
//     },
//     "yfinance": {
//       "command": "npx",
//       "args": ["-y", "@elektrothing/server-yahoofinance"]
//     },
//     "memory-bank": {
//       "command": "npx",
//       "args": ["-y", "@allpepper/memory-bank-mcp"],
//       "env": {
//         "MEMORY_BANK_ROOT": process.env.MEMORY_BANK_ROOT || "/Users/unrankedalzahrani/Desktop/finpal-svelte/memory-bank"
//       }
//     },
//     "memory": {
//       "command": "npx",
//       "args": ["-y", "@modelcontextprotocol/server-memory"]
//     }
//   }
// }; 