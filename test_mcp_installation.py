#TODO REMOVE FILE RESET API KEYS

import os
import sys
import importlib.util

def check_module(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {module_name} is NOT installed")
        return False
    else:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {module_name} is installed (version: {version})")
        return True

def check_node_modules(base_path):
    mcp_path = os.path.join(base_path, "node_modules", "@modelcontextprotocol")
    print(f"\nChecking MCP node modules in: {mcp_path}")
    
    if os.path.exists(mcp_path):
        print(f"✅ MCP node_modules directory exists")
        modules = [m for m in os.listdir(mcp_path) if not m.startswith('.')]
        print(f"Found {len(modules)} MCP modules:")
        for module in modules:
            module_path = os.path.join(mcp_path, module)
            if os.path.isdir(module_path):
                if os.path.exists(os.path.join(module_path, "dist", "index.js")):
                    print(f"✅ {module}: dist/index.js exists")
                else:
                    print(f"❌ {module}: dist/index.js MISSING")
    else:
        print(f"❌ MCP node_modules directory NOT found at {mcp_path}")

def check_config(config_path):
    print(f"\nChecking MCP config at: {config_path}")
    if os.path.exists(config_path):
        print(f"✅ MCP config file exists")
        with open(config_path, 'r') as f:
            content = f.read()
            print(f"Config file size: {len(content)} bytes")
            print(f"First 300 characters: {content[:300]}...")
    else:
        print(f"❌ MCP config file NOT found")

def main():
    print("MCP Installation Check")
    print("=====================")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check Python MCP modules
    print("\nChecking Python MCP modules:")
    check_module("pydantic_ai")
    check_module("pydantic_ai.mcp")
    check_module("mcp")
    
    # Check node modules
    base_path = os.getcwd()
    check_node_modules(base_path)
    
    # Check config file
    config_path = os.path.join(base_path, "backend", "mcp_config.json")
    check_config(config_path)
    
    # Check paths
    print("\nEnvironment PATH:")
    path = os.environ.get('PATH', '')
    paths = path.split(':')
    for p in paths:
        if 'node' in p or 'npm' in p:
            print(f"- {p}")
    
    # Check node and npm
    print("\nChecking node and npm:")
    node_path = os.popen('which node 2>/dev/null').read().strip()
    if node_path:
        print(f"✅ node found at: {node_path}")
        node_version = os.popen('node --version 2>/dev/null').read().strip()
        print(f"  node version: {node_version}")
    else:
        print("❌ node NOT found in PATH")
    
    npm_path = os.popen('which npm 2>/dev/null').read().strip()
    if npm_path:
        print(f"✅ npm found at: {npm_path}")
        npm_version = os.popen('npm --version 2>/dev/null').read().strip()
        print(f"  npm version: {npm_version}")
    else:
        print("❌ npm NOT found in PATH")
    
    npx_path = os.popen('which npx 2>/dev/null').read().strip()
    if npx_path:
        print(f"✅ npx found at: {npx_path}")
    else:
        print("❌ npx NOT found in PATH")

if __name__ == "__main__":
    main() 