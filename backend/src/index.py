# todo I believe unneeded cause of cloud functions
# Main entry point for our backend server
import os
import sys
import pathlib
import socket

# For local development, try to load dotenv, but this isn't needed on Render
# since environment variables are provided directly
try:
    from dotenv import load_dotenv
    load_dotenv()  # Only needed for local development
except ImportError:
    # This is fine in production where env vars are set directly
    pass

import uvicorn

# Add the current directory to the Python path to fix imports
current_dir = pathlib.Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()  # Get the parent directory (backend/)
sys.path.insert(0, str(current_dir))  # Add src/ to path
sys.path.insert(0, str(parent_dir))   # Add backend/ to path

# Determine environment (local vs Render)
def is_running_on_render():
    return os.environ.get("RENDER") == "true" or os.environ.get("IS_RENDER") == "true"

# Get machine hostname for logging
hostname = socket.gethostname()

# Environment detection
if is_running_on_render():
    env_type = "🌐 PRODUCTION (Render.com)"
    print("⚠️ Running on Render - MCP functionality may be limited due to server constraints")
else:
    env_type = "🖥️ LOCAL DEVELOPMENT"
    print("✅ Running locally - Full MCP functionality available with local servers")

# Priority is given to local MCP servers to avoid Render limitations
# See backend/src/services/pydantic_mcp_agent.py for MCP configuration priority

#todo remove later debugging Print paths for debugging
print(f"\n{'='*60}")
print(f"🚀 FinPal Backend Starting")
print(f"🔍 Environment: {env_type}")
print(f"💻 Hostname: {hostname}")
print(f"📁 Current directory: {current_dir}")
print(f"📂 Parent directory: {parent_dir}")
print(f"🔄 Python path: {sys.path}")
print(f"{'='*60}\n")

# import the api module - try both ways
try:
    import api
except ImportError:
    # If direct import fails, try with module prefix
    # from src import api
    pass

# Define the port
PORT = int(os.environ.get("PORT", 3002))  # Use PORT env var from Render.com or default to 3002

if __name__ == "__main__":
    print("Starting FinPal AI Backend...")
    print(f"Server will be available at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    # This format is required for reload=True to work
    # When using a relative import, we need to use the module format for api
    app_module = "src.api:app" if "src.api" in sys.modules else "api:app"
    print(f"Using app module: {app_module}")
    
    uvicorn.run(app_module, host="0.0.0.0", port=PORT, reload=True)
# NOTE: The old MCP command-line interface is still available:
# To run it: python -m services.pydantic_mcp_agent

