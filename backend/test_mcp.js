#!/usr/bin/env node

// this script tests the MCP configuration by generating the config
// and then testing that certain essential servers are included

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// First generate the config
console.log("Step 1: Generating MCP configuration...");
try {
  require('./generate-config.js');
  console.log("Config generation successful");
} catch (error) {
  console.error("Error generating config:", error);
  process.exit(1);
}

// Check that the config exists and has the correct content
console.log("\nStep 2: Verifying generated config...");
const configPath = path.join(__dirname, 'mcp_config.json');

try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  console.log("Config file parsed successfully");

  // Check for essential servers
  const essential = config.serverPriorities.essential || [];
  console.log(`Essential servers: ${essential.join(', ')}`);

  // Check autostart
  const autostartServers = [];
  for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
    if (serverConfig.autostart) {
      autostartServers.push(serverName);
    }
  }
  console.log(`Autostart servers: ${autostartServers.join(', ')}`);

  // Verify each essential server has correct settings
  let errors = false;
  for (const server of essential) {
    const serverConfig = config.mcpServers[server];
    if (!serverConfig) {
      console.error(`Error: Essential server "${server}" not found in mcpServers!`);
      errors = true;
      continue;
    }

    if (serverConfig.priority !== 'essential') {
      console.error(`Warning: Server "${server}" is in essential list but has priority "${serverConfig.priority}"`);
    }

    if (!serverConfig.autostart) {
      console.error(`Warning: Essential server "${server}" does not have autostart=true`);
    }
  }

  if (errors) {
    console.error("Errors found in configuration!");
    process.exit(1);
  } else {
    console.log("All essential servers configured correctly");
  }

} catch (error) {
  console.error("Error verifying config:", error);
  process.exit(1);
}

console.log("\nStep 3: Testing Python MCP agent...");
try {
  // Run a simple Python script to test MCP
  console.log("Running test_mcp.py...");
  const result = execSync('python test_mcp.py', { stdio: 'inherit' });
} catch (error) {
  console.error("Error running Python MCP test:", error);
} 