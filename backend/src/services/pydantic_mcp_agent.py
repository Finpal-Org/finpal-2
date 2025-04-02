from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from dotenv import load_dotenv
import asyncio
import pathlib
import sys
import os

# Set up paths to make imports work
current_dir = pathlib.Path(__file__).parent.resolve()
backend_dir = current_dir.parent.parent
sys.path.insert(0, str(backend_dir))

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.gemini import GeminiModel
    from pydantic_ai.providers.google_gla import GoogleGLAProvider
except ImportError:
    print("Error: Required packages not found. Please install with:")
    print("pip install pydantic-ai python-dotenv rich")
    sys.exit(1)

# Import the MCPClient
MCPClient = None
try:
    # First try the dot import (when running as module)
    from .mcp_client import MCPClient
except (ImportError, ValueError):
    try:
        # Then try absolute import (when running as script)
        from services.mcp_client import MCPClient
    except (ImportError, ValueError):
        print("Warning: MCP client not found. Tools will not be available.")

# Get the directory where the current script is located
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

# Define the path to the config file relative to the script directory
CONFIG_FILE = r"C:\Users\Unran\Desktop\finpal-svelte\backend\mcp_config.json"
# or alternatively:
# CONFIG_FILE = "C:/Users/Unran/Desktop/finpal-svelte/backend/mcp_config.json"

# Load environment variables from both root and backend directory
root_env_path = pathlib.Path(__file__).parent.parent.parent.parent / '.env'
backend_env_path = pathlib.Path(__file__).parent.parent.parent / '.env'

# Try to load from root first, then from backend directory
load_dotenv(dotenv_path=root_env_path)
load_dotenv(dotenv_path=backend_env_path, override=True)

#  "gemini-1.5-flash",
#     "gemini-1.5-flash-8b",
#     "gemini-1.5-pro",
#     "gemini-1.0-pro",
#     "gemini-2.0-flash-exp",
#     "gemini-2.0-flash-thinking-exp-01-21",
#     "gemini-exp-1206",
#     "gemini-2.0-flash",
#     "gemini-2.0-flash-lite-preview-02-05",
#     "gemini-2.0-pro-exp-02-05",

def get_model():
    # Use the proper model and explicitly pass the API key
    model_name = os.getenv('MODEL_CHOICE', 'gemini-2.0-flash').replace('google-gla:', '')
    api_key = os.getenv('LLM_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("ERROR: No API key found for the AI model!")
        print("Please set LLM_API_KEY or GEMINI_API_KEY in your .env file")
        
    # Explicitly pass the API key rather than relying on environment detection
    return GeminiModel(
        model_name, 
        provider=GoogleGLAProvider(api_key=api_key),
        generation_config={"temperature": 0.3}
    )

# IMPORTANT: The function that gets the agent for other files to use
async def get_pydantic_ai_agent():
    """
    Create and return a Pydantic AI agent with all MCP tools.
    This is the main function used by the API to get an agent instance.
    """
    if MCPClient is None:
        print("Warning: Using AI agent without MCP tools")
        return None, Agent(model=get_model())
    
    try:
        # Initialize MCP client with all tools from config
        client = MCPClient()
        client.load_servers(str(CONFIG_FILE))
        tools = await client.start()
        print(f"Loaded {len(tools)} MCP tools: {', '.join(t.name for t in tools) if tools else 'none'}")
        return client, Agent(model=get_model(), tools=tools)
    except Exception as e:
        print(f"Error initializing MCP client: {e}")
        print("Falling back to AI agent without tools")
        return None, Agent(model=get_model())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ Main Function with CLI Chat ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main():
    print("=== Pydantic AI MCP CLI Chat ===")
    print("Type 'exit' to quit the chat")
    
    model_choice = os.getenv('MODEL_CHOICE', 'gemini-2.0-flash')
    api_key = os.getenv('LLM_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    print(f"Initializing with model: {model_choice}")
    # Mask API key for debug purposes
    if api_key:
        masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        print(f"API key found (masked): {masked_key}")
    else:
        print("WARNING: No API key found! Please check your .env file.")
    
    print("Loading MCP tools and starting chat agent...")
    
    # Initialize the agent and message history
    mcp_client_instance, mcp_agent = await get_pydantic_ai_agent()
    console = Console()
    messages = []
    
    try:
        while True:
            sys.stdout.flush()
            user_input = input("\n[You] ")
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Goodbye!")
                break
            
            try:
                # Process the user input and output the response
                print("\n[Assistant]")
                async with mcp_agent.run_stream(
                    user_input, message_history=messages
                ) as result:
                    async for message in result.stream_text(delta=True):
                        print(message, end="", flush=True)
                print()  # newline after streaming
                messages.extend(result.all_messages())
                
            except Exception as e:
                print(f"\n[Error] An error occurred: {str(e)}")
    except KeyboardInterrupt:
        print("\nExiting chat...")
    finally:
        # Ensure proper cleanup of MCP client resources when exiting
        if mcp_client_instance:
            await mcp_client_instance.cleanup()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())