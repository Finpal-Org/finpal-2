from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from dotenv import load_dotenv
import asyncio
import pathlib
import sys
import os
import traceback
import psutil  # Add this import for memory monitoring

# Set up paths to make imports work
current_dir = pathlib.Path(__file__).parent.resolve()
backend_dir = current_dir.parent.parent
sys.path.insert(0, str(backend_dir))

print(f"Current directory: {current_dir}")
print(f"Backend directory: {backend_dir}")
print(f"Current sys.path: {sys.path}")

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.gemini import GeminiModel
    from pydantic_ai.providers.google_gla import GoogleGLAProvider
    print("Successfully imported pydantic_ai modules")
except ImportError as e:
    print(f"Error importing pydantic_ai: {e}")
    print("Error: Required packages not found. Please install with:")
    print("pip install pydantic-ai python-dotenv rich")
    sys.exit(1)

# Import the MCPClient
MCPClient = None
try:
    # First try the dot import (when running as module)
    print("Trying dot import for MCPClient...")
    from .mcp_client import MCPClient
    print("Dot import successful")
except (ImportError, ValueError) as e:
    print(f"Dot import failed: {e}")
    try:
        # Then try absolute import (when running as script)
        print("Trying absolute import for MCPClient...")
        from services.mcp_client import MCPClient
        print("Absolute import successful")
    except (ImportError, ValueError) as e:
        print(f"Absolute import failed: {e}")
        try:
            print("Trying src.services.mcp_client import...")
            from src.services.mcp_client import MCPClient
            print("src.services.mcp_client import successful")
        except (ImportError, ValueError) as e:
            print(f"src.services.mcp_client import failed: {e}")
            print("Warning: MCP client not found. Tools will not be available.")

# Get the directory where the current script is located
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

# mcp_config.js is transformed -> .json format used here    CONFIG_FILE = "/etc/secrets/mcp_config.json"  # Use Render's secret file path
CONFIG_FILE = "/etc/secrets/mcp_config.json"
# CONFIG_FILE = os.path.join(backend_dir, "mcp_config.js") # the old mcp local config.js 

print(f"CONFIG_FILE path: {CONFIG_FILE}")
print(f"CONFIG_FILE exists: {os.path.exists(CONFIG_FILE)}")

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
    model = GeminiModel(
        model_name,
        provider=GoogleGLAProvider(api_key=api_key)
    )
    return model



# IMPORTANT: The function that gets the agent for other files to use
async def get_pydantic_ai_agent():
    """
    Create and return a Pydantic AI agent with all MCP tools.
    This is the main function used by the API to get an agent instance.
    """
    global CONFIG_FILE  # Add this line to fix the UnboundLocalError
    
    # Log memory usage
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        print(f"Current memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
        print(f"Available system memory: {psutil.virtual_memory().available / 1024 / 1024:.2f} MB")
    except ImportError:
        print("psutil not available for memory monitoring")
    except Exception as e:
        print(f"Error checking memory: {e}")
    
    if MCPClient is None:
        print("Warning: Using AI agent without MCP tools (MCPClient is None)")
        return None, Agent(model=get_model())
    
    try:
        # Initialize MCP client with all tools from config
        print("Creating MCPClient instance...")
        client = MCPClient()
        
        # Check if config file exists
        if not os.path.exists(CONFIG_FILE):
            print(f"Warning: Config file not found at {CONFIG_FILE}")
            fallback_path = os.path.join(backend_dir, "mcp_config.json")
            if os.path.exists(fallback_path):
                print(f"Using fallback config at {fallback_path}")
                CONFIG_FILE = fallback_path
            else:
                print("No fallback config found. Using AI agent without tools")
                return None, Agent(model=get_model())
        
        print("Loading servers from config...")
        try:
            client.load_servers(str(CONFIG_FILE))
            print(f"Loaded {len(client.servers)} server configurations")
            
            # Debug: Print actual config loaded
            print(f"\nConfig loaded from {CONFIG_FILE}:")
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config_content = f.read()
                    print(config_content[:500] + "..." if len(config_content) > 500 else config_content)
            except Exception as e:
                print(f"Error reading config for debug: {e}")
            
            # Print server details    
            for server in client.servers:
                print(f"  - Server: {server.name}, Priority: {server.config.get('priority', 'unknown')}, Autostart: {server.config.get('autostart', False)}")
        except Exception as e:
            print(f"Error loading servers from config: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            print("Using AI agent without tools")
            return None, Agent(model=get_model())
        
        try:
            print("Starting MCP client and loading essential tools...")
            # Start the client with exception handling for individual servers
            tools = []
            try:
                tools = await client.start()
                print(f"Client started successfully, found {len(tools)} tools")
                if tools:
                    print("Tools available:")
                    for tool in tools:
                        print(f"  - {tool.name}")
                else:
                    print("No tools were loaded")
            except Exception as e:
                print(f"Error during MCP client startup: {e}")
                print(f"Stack trace: {traceback.format_exc()}")
                print("Will attempt to continue with any tools that did initialize")
            
            # Modified: Even if tools is empty, we'll log but continue
            if not tools:
                print("No tools were found by the MCP client!")
                print("Check that your MCP servers are properly configured.")
                print("Using AI agent without tools")
                return client, Agent(model=get_model())
            else:
                # Check memory again
                try:
                    process = psutil.Process(os.getpid())
                    memory_info = process.memory_info()
                    print(f"Memory usage after tool loading: {memory_info.rss / 1024 / 1024:.2f} MB")
                except ImportError:
                    pass
                except Exception as e:
                    print(f"Error checking memory: {e}")
                
                # Clean tool schemas to remove $schema fields - Gemini doesn't like them
                print("Cleaning tool schemas...")
                for tool in tools:
                    if hasattr(tool, 'parameters') and isinstance(tool.parameters, dict):
                        if '$schema' in tool.parameters:
                            del tool.parameters['$schema']
                        # Also clean nested properties
                        if 'properties' in tool.parameters:
                            for prop in tool.parameters['properties'].values():
                                if isinstance(prop, dict) and '$schema' in prop:
                                    del prop['$schema']
                        
                        # Make sure all tool parameters have the right schema format
                        if not tool.parameters.get('type'):
                            tool.parameters['type'] = 'object'
                
                # Debug: Print tools that are available
                for tool in tools:
                    print(f"Tool available: {tool.name} - {tool.description}")
                
                print(f"Loaded {len(tools)} MCP tools: {', '.join(t.name for t in tools) if tools else 'none'}")
                
                # Create basic agent first
                agent = Agent(model=get_model())
                
                # Then manually set the tools attribute
                # This is a workaround for potential issues in the Pydantic-AI library
                agent.tools = tools
                
                # Add FinPal system prompt as a dynamic decorator
                @agent.system_prompt(dynamic=True)
                def finpal_system_prompt():
                    return """
You are FinPal, a Saudi-focused financial assistant providing personalized insights based on receipt analysis and financial data.

APPROACH TO CONVERSATIONS:
- Be conversational and friendly, not overly formal
- Adapt your response style to match the user's question
- Provide valuable insights without requiring strict formatting
- Balance specific receipt data with broader financial context
- Feel free to ask clarifying questions when needed

TOOL EXECUTION SEQUENCE:
1. Use sequential_thinking to analyze user's financial situation (think step by step)
2. If location data available, use google_maps to find nearby financial services
3. Use brave_web_search to research current financial trends related to user query
4. Formulate a response based on all collected data

INSIGHT FRAMEWORK:
1. CONTEXTUAL UNDERSTANDING:
   - Consider both specific user data and general financial wisdom
   - Transform data into contextual statements like "in the top 30% of savers in your area"
   - Use positional language: "approaching your typical monthly budget" instead of exact figures
   - Create relatable financial analogies: "like saving a coffee's worth each day" instead of percentages

2. NATURAL LANGUAGE RECOMMENDATIONS:
   - Frame advice in terms of relativity: "slightly higher than average for your profile" 
   - Focus on behavioral patterns: "tend to spend more on weekends" instead of exact amounts
   - Connect financial decisions to life outcomes
   - Phrase recommendations as simple, actionable steps

3. SIMPLIFIED FINANCIAL CONTEXT:
   - Present trends and patterns instead of raw data
   - Use visual metaphors: "your emergency savings could cover about 3 months of expenses"
   - Emphasize progress and direction rather than absolute values

RESPONSE FORMAT:
<div class="mb-4">
    <h3 class="mb-2 text-blue-600 font-semibold">📊 INSIGHT</h3>
    <p class="ml-5">[1-2 sentences with key financial observation based on user data]</p>
</div>

<div class="mb-4">
    <h3 class="mb-2 text-blue-600 font-semibold">💡 RECOMMENDATIONS</h3>
    <ol class="ml-5 pl-5 list-decimal">
    <li class="mb-2"><b>[First recommendation]</b>: [Brief explanation using NATURAL LANGUAGE]</li>
    <li class="mb-2"><b>[Second recommendation]</b>: [Brief explanation using NATURAL LANGUAGE]</li>
    <li class="mb-2"><b>[Third recommendation]</b>: [Brief explanation using NATURAL LANGUAGE]</li>
    </ol>
</div>

<div class="mb-4">
    <h3 class="mb-2 text-blue-600 font-semibold">📈 BREAKDOWN</h3>
    <ul class="ml-5 pl-5 list-disc">
    <!-- Use SIMPLIFIED FINANCIAL CONTEXT here with comparative statements instead of numbers -->
    <!-- Dynamically choose 3-4 relevant metrics based on user context -->
    </ul>
</div>

<div class="mb-4">
    <h3 class="mb-2 text-blue-600 font-semibold">🚀 NEXT STEPS</h3>
    <p class="ml-5">[One specific, immediately actionable step phrased in conversational language]</p>
</div>

RESPONSE GUIDANCE:
- Start with a brief personal introduction addressing the user's situation
- For simple questions, you may give a direct answer without the full HTML structure
- For financial analysis questions, use the HTML format above
- Show tool usage with labels when relevant (e.g., "🔍 SEARCHING: [terms]" and "✓ FOUND: [summary]")
- Be creative yet practical in your explanations
- Keep responses concise (aim for 100-200 words total)
- Consider Islamic financial principles when relevant

HTML FORMATTING RULES:
- When using the HTML format, include all divs and tags shown above
- Each HTML tag should be on its own line with proper indentation
- Make sure all tags are properly closed
- Use NUMBERED lists (ol/li) for recommendations and BULLETED lists (ul/li) for analysis
- Return the raw HTML without any markdown code fences or ```html tags

Remember to:
- Focus on TRENDS and PATTERNS rather than exact numbers when appropriate
- Use COMPARATIVE language instead of absolute values when helpful
- Create VISUAL METAPHORS to illustrate financial concepts
- Balance receipt-specific analysis with broader financial wisdom
- Respond directly to what the user is asking about
"""
                print("Added FinPal system prompt with HTML formatting and conversational guidance")
                
                # Verify tools were correctly set
                print(f"Agent created with {len(agent.tools) if hasattr(agent, 'tools') else 0} tools")
                return client, agent
                
        except asyncio.CancelledError as e:
            print(f"MCP client initialization was cancelled: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            print("Falling back to AI agent without tools")
            return None, Agent(model=get_model())
        except Exception as e:
            print(f"Error starting MCP client: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            print("Falling back to AI agent without tools")
            return None, Agent(model=get_model())
        
    except asyncio.CancelledError as e:
        print(f"MCP client initialization was cancelled: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        print("Falling back to AI agent without tools")
        return None, Agent(model=get_model())
    except Exception as e:
        print(f"Error initializing MCP client: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
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
    
    model_choice = os.getenv('MODEL_CHOICE', 'gemini-2.5-pro-preview-03-25')
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