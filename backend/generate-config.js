// Script to generate mcp_config.json from mcp_config.js
const fs = require('fs');
const path = require('path');
const config = require('./mcp_config');

// Write the config to a JSON file
fs.writeFileSync(
  path.join(__dirname, 'mcp_config.json'),
  JSON.stringify(config, null, 2),
  'utf8'
);

console.log('Successfully generated mcp_config.json with environment variables'); 