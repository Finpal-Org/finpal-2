# todo I believe unneeded cause of cloud functions
# Main entry point for our backend server
import os
import sys
import pathlib

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
sys.path.insert(0, str(current_dir))

# import the api module
import api

# Define the port
PORT = int(os.environ.get("PORT", 3002))  # Use PORT env var from Render.com or default to 3002

if __name__ == "__main__":
    print("Starting FinPal AI Backend...")
    print(f"Server will be available at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    # This format is required for reload=True to work
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, reload=True)
# NOTE: The old MCP command-line interface is still available:
# To run it: python -m services.pydantic_mcp_agent

