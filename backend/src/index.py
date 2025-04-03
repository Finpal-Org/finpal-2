# Main entry point for our backend server
import os
import sys
import pathlib
from dotenv import load_dotenv
import uvicorn

# Add the current directory to the Python path to fix imports
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

# Now import the api module
import api

# Load environment variables from .env file (API keys, etc.)
load_dotenv()

# Define the port
PORT = 3002  # Changed from 3001 to avoid conflicts

if __name__ == "__main__":
    print("Starting FinPal AI Backend...")
    print(f"Server will be available at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    # This format is required for reload=True to work
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, reload=True)
# NOTE: The old MCP command-line interface is still available:
# To run it: python -m services.pydantic_mcp_agent

