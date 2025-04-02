# Main entry point for our backend server
import os
import sys
import pathlib
from dotenv import load_dotenv
import uvicorn

# Add the current directory to the Python path to fix imports
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

# Load environment variables from .env file (API keys, etc.)
load_dotenv()

if __name__ == "__main__":
    print("Starting FinPal AI Backend...")
    print("Server will be available at: http://localhost:3001")
    print("Press Ctrl+C to stop the server")
    
    # Start the FastAPI server using uvicorn
    # - "api:app" means "import the 'app' from the 'api.py' file
    # - reload=True means the server will auto-refresh when code changes (great for development)
    uvicorn.run("api:app", host="0.0.0.0", port=3001, reload=True)
    
# NOTE: The old MCP command-line interface is still available:
# To run it: python -m services.pydantic_mcp_agent

