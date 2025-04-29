// #!/usr/bin/env node

// const fs = require('fs');
// const path = require('path');

// // Get environment variables and paths
// const isProduction = process.env.NODE_ENV === 'production';
// const configPath = process.env.MCP_CONFIG_PATH || path.join(__dirname, 'mcp_config.json');

// console.log(`Generating MCP config file at: ${configPath}`);
// console.log(`Environment: ${isProduction ? 'Production' : 'Development'}`);

// // Create optimized configuration for Render deployment
// const config = {
//   "mcpServers": {
//     "brave-search": {
//       "command": "docker",
//       "args": ["run", "--rm", "-i", "--memory=96m", "--memory-swap=96m", "modelcontextprotocol/brave-search"],
//       "env": {
//         "BRAVE_API_KEY": process.env.BRAVE_API_KEY || "BSAMKgBTwIL9Qr0fUwQh3ekht3U32Sn"
//       },
//       "priority": "important",
//       "autostart": true,
//       "allowedTools": ["brave_web_search", "brave_local_search"]
//     },
//     "sequential-thinking": {
//       "command": "npx",
//       "args": ["-y", "--max-old-space-size=64", "@modelcontextprotocol/server-sequential-thinking"],
//       "priority": "essential",
//       "autostart": true,
//       "allowedTools": ["sequentialthinking"]
//     },
//     "google-maps": {
//       "command": "npx",
//       "args": ["-y", "--max-old-space-size=64", "@modelcontextprotocol/server-google-maps"],
//       "env": {
//         "GOOGLE_MAPS_API_KEY": process.env.GOOGLE_MAPS_API_KEY || "AIzaSyB2kxDjle7yKIVJjoNVKw5vMkENy9TljQQ"
//       },
//       "priority": "important",
//       "autostart": false,
//       "allowedTools": ["findPlace", "searchNearby"]
//     },
//     "memory": {
//       "command": "npx",
//       "args": ["-y", "--max-old-space-size=64", "@modelcontextprotocol/server-memory"],
//       "priority": "essential",
//       "autostart": true,
//       "allowedTools": [
//         "read_graph",
//         "search_nodes",
//         "create_entities",
//         "add_observations",
//         "open_nodes",
//         "create_relations"
//       ]
//     },
//     "yfinance": {
//       "command": "npx",
//       "args": ["-y", "--max-old-space-size=64", "@elektrothing/server-yahoofinance"],
//       "priority": "optional",
//       "autostart": false,
//       "allowedTools": ["getQuote", "getHistory"]
//     }
//   },
//   "serverPriorities": {
//     "essential": ["memory", "sequential-thinking"],
//     "important": ["google-maps", "brave-search"],
//     "optional": ["yfinance"]
//   }
// };

// // Write the config file
// try {
//   fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
//   console.log(`Successfully generated MCP config at: ${configPath}`);

//   // Verify the file was created
//   if (fs.existsSync(configPath)) {
//     console.log(`Verified config file exists at: ${configPath}`);
//     console.log(`File size: ${fs.statSync(configPath).size} bytes`);
//   } else {
//     console.error(`ERROR: Failed to verify config file at: ${configPath}`);
//   }
// } catch (error) {
//   console.error(`ERROR: Failed to write config file: ${error.message}`);
//   process.exit(1);
// } 