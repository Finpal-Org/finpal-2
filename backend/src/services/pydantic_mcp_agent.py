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
from typing import TypedDict, Dict, Any, List
import time
import json

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

# Define possible configuration file paths
RENDER_CONFIG_PATH = "/etc/secrets/mcp_config.json"  # Render's secret file path
LOCAL_CONFIG_PATH = os.path.join(backend_dir, "mcp_config.json")  # Local path (generated JSON)
LOCAL_CONFIG_JS_PATH = os.path.join(backend_dir, "mcp_config.js")  # Local JS config file path

# Global variable to store cached receipt context
_cached_receipt_context = None
_last_receipt_refresh = 0
_receipt_cache_ttl = 15 * 60  # 15 minutes in seconds

# Check environment and set appropriate config file path
def get_config_file_path():
    # Check if the MCP_CONFIG_PATH environment variable is set
    env_config_path = os.environ.get('MCP_CONFIG_PATH')
    if env_config_path and os.path.exists(env_config_path):
        print(f"Using config path from environment variable: {env_config_path}")
        return env_config_path
    
    # Check for local JSON file first - prioritize local over Render
    if os.path.exists(LOCAL_CONFIG_PATH):
        print(f"Using local JSON config: {LOCAL_CONFIG_PATH}")
        return LOCAL_CONFIG_PATH
    
    # Check for Render's secret file path as fallback
    if os.path.exists(RENDER_CONFIG_PATH):
        print(f"Using Render config path: {RENDER_CONFIG_PATH}")
        return RENDER_CONFIG_PATH
    
    # If JS file exists but JSON doesn't, log a warning
    if os.path.exists(LOCAL_CONFIG_JS_PATH):
        print(f"Found JS config but no JSON config. Please run 'node generate-config.js' in the backend directory")
        print(f"Defaulting to: {LOCAL_CONFIG_PATH}")
        return LOCAL_CONFIG_PATH
    
    # No config found - log warning and return the local path as default
    print("WARNING: No configuration file found. Please create a mcp_config.json file")
    return LOCAL_CONFIG_PATH

# Set the config file path
CONFIG_FILE = get_config_file_path()

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

class _GeminiPartUnion(TypedDict, total=False):
    text: Dict[str, Any] | str  # Allow for either text as string or as a dict with additional fields
    function_call: Dict[str, Any]
    function_response: Dict[str, Any]
    executableCode: Dict[str, Any]  # Support for executableCode type

# Function to handle Gemini responses that might have executableCode but missing text field
def extract_text_from_gemini_part(part: Dict[str, Any]) -> str:
    # If text field exists, return it directly
    if 'text' in part:
        if isinstance(part['text'], str):
            return part['text']
        elif isinstance(part['text'], dict) and 'text' in part['text']:
            return part['text']['text']
    
    # If executableCode exists but no text field, convert code to text
    if 'executableCode' in part:
        code_part = part['executableCode']
        if isinstance(code_part, dict):
            code = code_part.get('code', '')
            lang = code_part.get('lang', '')
            return f"```{lang}\n{code}\n```"
    
    # Default case if no recognizable content is found
    return ""

def get_model():
    # Use the proper model and explicitly pass the API key
    model_name = os.getenv('MODEL_CHOICE', 'gemini-2.5-pro-preview-03-25').replace('google-gla:', '')
    api_key = os.getenv('LLM_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("ERROR: No API key found for the AI model!")
        print("Please set LLM_API_KEY or GEMINI_API_KEY in your .env file")
        
    # Explicitly pass the API key rather than relying on environment detection
    model = GeminiModel(
        model_name,
        provider=GoogleGLAProvider(api_key=api_key)
    )
    
    # Monkey patch the _process_response method to handle executableCode
    original_process_response = model._process_response
    
    def patched_process_response(self, response_data, **kwargs):
        try:
            # Try the original method first
            return original_process_response(response_data, **kwargs)
        except Exception as e:
            print(f"Error in original _process_response: {e}")
            print(f"Response data structure: {json.dumps(response_data, indent=2)[:500]}...")
            # If there's a validation error related to missing text field, try to extract text from executableCode
            if "text.text Field required" in str(e):
                print("Attempting to fix missing text field by extracting from executableCode")
                try:
                    # Access the candidates in the response data
                    if "candidates" in response_data and len(response_data["candidates"]) > 0:
                        candidate = response_data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            # Process each part in the response
                            for i, part in enumerate(candidate["content"]["parts"]):
                                print(f"Processing part {i}: {json.dumps(part, indent=2)[:200]}...")
                                # If part has executableCode but no text, add a text field
                                if "executableCode" in part and "text" not in part:
                                    code_part = part["executableCode"]
                                    code = code_part.get("code", "")
                                    lang = code_part.get("lang", "")
                                    print(f"Adding text field with code of length {len(code)} and lang {lang}")
                                    part["text"] = f"```{lang}\n{code}\n```"
                    # Try processing again with modified data
                    return original_process_response(response_data, **kwargs)
                except Exception as fix_error:
                    print(f"Error fixing response: {fix_error}")
                    # If our fix fails, re-raise the original error
                    raise e
            # Re-raise the original exception for other errors
            raise
    
    # Apply the monkey patch
    model._process_response = patched_process_response.__get__(model, type(model))
    
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
        
        # Check if config file exists (should be already verified but check again)
        if not os.path.exists(CONFIG_FILE):
            print(f"Warning: Config file not found at {CONFIG_FILE}")
            print("Using AI agent without tools")
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
                    global _cached_receipt_context, _last_receipt_refresh
                    
                    # Get current time for cache comparison
                    current_time = time.time()
                    
                    # Check if we have cached context and it's still valid
                    if _cached_receipt_context is None or (current_time - _last_receipt_refresh) > _receipt_cache_ttl:
                        try:
                            # Import here to avoid circular imports
                            from src.services.direct_context import fetch_receipt_context
                            # Fetch receipt context and update cache
                            _cached_receipt_context = fetch_receipt_context(limit=150) 
                            _last_receipt_refresh = current_time
                            print(f"Successfully fetched receipt context ({len(_cached_receipt_context)} characters)")
                        except Exception as e:
                            print(f"Error fetching receipt context: {e}")
                            # If we have cache, use it even if expired on error
                            if _cached_receipt_context is None:
                                _cached_receipt_context = "No receipt data available."
                            else:
                                print("Using expired cached receipt context due to error")
                    else:
                        print(f"Using cached receipt context ({len(_cached_receipt_context)} characters)")
                    
                    # Use the cached context
                    receipt_context = _cached_receipt_context
                    
                    # todo apply formating even if mcp servers arent setup, skip usage of servers if empty.
                    base_prompt = """
You are FinPal, a Saudi-focused financial assistant providing personalized insights based on receipt analysis and financial data.

DYNAMIC TOOL SELECTION:

MANDATORY TOOL USAGE:
IMPORTANT: You MUST use at least these two tools for EVERY query:
1. sequential_thinking - Use this tool first to break down the user's request and analyze how to approach it
2. memory - Use this to recall context from previous interactions 

You must ALWAYS include both your thinking process AND a clear response in your answers. Never put all useful information only in the thinking part.

AVAILABLE TOOLS AND THEIR CAPABILITIES:
The following tools are at your disposal. Choose the most appropriate tools based on the user's query and the specific task requirements:

1. sequential_thinking: Helps break down complex problems step-by-step, useful for analyzing financial data, planning budgets, or solving multi-part questions.

2. memory: Stores and retrieves user context and conversation history, valuable for providing personalized responses based on past interactions.

3. brave_search: Provides up-to-date information from the web, ideal for current events, market trends, or researching specific topics not in your training data.

4. google_maps: Offers location-based services, useful for comparing merchants by proximity, finding nearby businesses, or providing geographical context.

5. yfinance: Accesses market data and financial information, excellent for stock analysis, market trends, and investment questions.

TOOL SELECTION GUIDANCE:
- Prioritize tools based on the nature of the query
- Consider combining tools for comprehensive answers 
- Use only what's needed - not every query requires tools
- Always formulate responses based on all available receipt data context from your LLM cache
- When using tools, process their output thoughtfully before responding
- ALWAYS use brave_search for most queries to get the latest information
- NEVER display receipt IDs in responses - only refer to merchants by name for privacy/security
- For opinions about Saudi Arabia or other countries, specifically search Reddit (e.g., "Reddit Saudi Arabia [topic]")
- For economic questions, ALWAYS use both brave_search AND yfinance tools together

Example Tool Combinations:
• For spending analysis: memory (for past data) + brave_search (for context) + sequential_thinking (for analysis)
• For investment advice: yfinance (market data) + brave_search (latest news) + sequential_thinking (analysis)
• For location-based places comparisons: google_maps (location data) + brave_search (reviews and opinions) + memory (user preferences). suggest alternative places with good rating 4+ star and cheaper on average on google maps.
• For economic outlook questions: brave_search (economic news) + yfinance (market data) + sequential_thinking (analysis). use stock market status in ksa , infaltion, spending trends & worlds news / opinions on the economy. always provide source and scientific base for any economic suggestions.    
• For opinions or recommendations: brave_search with specific sources like "Reddit Saudi Arabia [topic]" for local insights
• For simple factual questions: brave_search to ensure up-to-date information

When multiple tools could be helpful, use your judgment about order and relevance. Aim to provide valuable insights while being efficient with tool usage.

APPROACH TO CONVERSATIONS:
- Be conversational and friendly, not overly formal
- Adapt your response style to match the user's question
- Provide valuable insights without requiring strict formatting
- Balance specific receipt data with broader financial context
- Keep responses concise and meaningful
- Feel free to ask clarifying questions when needed

DYNAMIC RESPONSE FORMATTING:
First, analyze the user's intent and query type, then select ONE of the following format templates:

# FORMAT 1: COMPREHENSIVE ANALYSIS
USE WHEN: User wants overall spending insights, monthly summaries, budget reviews, or general financial health assessment.
```html
<div class="mb-4 p-4 bg-blue-50 rounded-lg">
    <h3 class="mb-2 text-blue-600 font-semibold">📊 FINANCIAL SNAPSHOT</h3>
    <p class="ml-5">[1-2 concise sentences with key financial observation]</p>
    
    <h3 class="mb-2 mt-4 text-blue-600 font-semibold">💡 RECOMMENDATIONS</h3>
    <ol class="ml-5 pl-5 list-decimal">
        <li class="mb-2"><b>[First recommendation]</b>: [Brief explanation]</li>
        <li class="mb-2"><b>[Second recommendation]</b>: [Brief explanation]</li>
        <li class="mb-2"><b>[Third recommendation]</b>: [Brief explanation]</li>
    </ol>
    
    <h3 class="mb-2 mt-4 text-blue-600 font-semibold">📈 SPENDING BREAKDOWN</h3>
    <div class="ml-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-3 border rounded bg-muted">
            <h4 class="font-medium text-gray-700">Top Categories</h4>
            <ul class="pl-5 list-disc">
                <li>[Category 1] - [percentage]</li>
                <li>[Category 2] - [percentage]</li>
                <li>[Category 3] - [percentage]</li>
            </ul>
        </div>
        <div class="p-3 border rounded bg-muted">
            <h4 class="font-medium text-gray-700">Monthly Trend</h4>
            <p>[Brief trend description with comparative language]</p>
        </div>
    </div>
    
    <h3 class="mb-2 mt-4 text-blue-600 font-semibold">🚀 NEXT STEPS</h3>
    <p class="ml-5">[One specific, actionable step]</p>
</div>
```

# FORMAT 2: DIRECT ANSWER
USE WHEN: User asks a specific question about a particular receipt, category, or transaction.
```html
<div class="mb-4 p-4 bg-gray-50 rounded-lg">
    <h3 class="mb-2 text-blue-600 font-semibold">💬 ANSWER</h3>
    <p class="ml-5">[Clear, direct answer to the specific question]</p>
    
    <div class="mt-3 ml-5 p-3 border-l-4 border-blue-400 bg-blue-50">
        <p class="text-sm italic">[Additional context or relevant detail if needed]</p>
    </div>
    
    <h3 class="mb-2 mt-4 text-blue-600 font-semibold">💡 RELATED INSIGHT</h3>
    <p class="ml-5">[One relevant financial insight related to the question]</p>
</div>
```

# FORMAT 3: TREND ANALYSIS
USE WHEN: User is asking about spending patterns, financial forecasts, or historical comparisons.
```html
<div class="mb-4 p-4 bg-purple-50 rounded-lg">
    <h3 class="mb-2 text-purple-600 font-semibold">📈 TREND ANALYSIS</h3>
    <p class="ml-5">[Summary of identified trend]</p>
    
    <h3 class="mb-2 mt-4 text-purple-600 font-semibold">📅 TIMELINE</h3>
    <div class="ml-5 flex flex-col space-y-2">
        <div class="flex items-center">
            <span class="w-24 font-medium">Past:</span>
            <span>[Historical data point or pattern]</span>
        </div>
        <div class="flex items-center">
            <span class="w-24 font-medium">Present:</span>
            <span>[Current status]</span>
        </div>
        <div class="flex items-center">
            <span class="w-24 font-medium">Forecast:</span>
            <span>[Projected pattern with confidence indication]</span>
        </div>
    </div>
    
    <h3 class="mb-2 mt-4 text-purple-600 font-semibold">🔍 FACTORS</h3>
    <ul class="ml-5 pl-5 list-disc">
        <li>[First factor influencing the trend]</li>
        <li>[Second factor influencing the trend]</li>
        <li>[Third factor influencing the trend]</li>
    </ul>
    
    <h3 class="mb-2 mt-4 text-purple-600 font-semibold">🚀 RECOMMENDATION</h3>
    <p class="ml-5">[Strategic recommendation based on the trend]</p>
</div>
```

# FORMAT 4: COMPARATIVE ANALYSIS
USE WHEN: User is asking for comparisons between merchants, categories, time periods, or against averages.
```html
<div class="mb-4 p-4 bg-green-50 rounded-lg">
    <h3 class="mb-2 text-green-600 font-semibold">⚖️ COMPARISON</h3>
    <p class="ml-5">[Summary of what's being compared and key finding]</p>
    
    <div class="ml-5 mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-3 border rounded bg-muted">
            <h4 class="font-medium text-gray-700">[First item]</h4>
            <ul class="pl-5 list-disc">
                <li>[Metric 1]: [Value]</li>
                <li>[Metric 2]: [Value]</li>
                <li>[Metric 3]: [Value]</li>
            </ul>
        </div>
        <div class="p-3 border rounded bg-muted">
            <h4 class="font-medium text-gray-700">[Second item]</h4>
            <ul class="pl-5 list-disc">
                <li>[Metric 1]: [Value]</li>
                <li>[Metric 2]: [Value]</li>
                <li>[Metric 3]: [Value]</li>
            </ul>
        </div>
    </div>
    
    <h3 class="mb-2 mt-4 text-green-600 font-semibold">🔑 KEY DIFFERENCES</h3>
    <ul class="ml-5 pl-5 list-disc">
        <li>[First significant difference]</li>
        <li>[Second significant difference]</li>
    </ul>
    
    <h3 class="mb-2 mt-4 text-green-600 font-semibold">💡 RECOMMENDATION</h3>
    <p class="ml-5">[Practical advice based on the comparison]</p>
</div>
```

# FORMAT 5: QUICK RESPONSE
USE WHEN: User has a simple question requiring a brief response, or is asking for clarification.
```html
<div class="p-4 bg-gray-50 rounded-lg">
    <p class="text-lg">[Clear, concise answer without formal structure]</p>
</div>
```

# FORMAT 6: DATA VISUALIZATION
USE WHEN: User requests visualizations, charts, or graphical representations of their financial data.
```html
<div class="mb-4 p-4 bg-yellow-50 rounded-lg">
    <h3 class="mb-2 text-yellow-600 font-semibold">📊 DATA VISUALIZATION</h3>
    <p class="ml-5">[Brief description of what the visualization shows]</p>
    
    <div class="ml-5 mt-4 p-3 border rounded bg-muted">
        <div id="chart-container-CHART_ID" style="width: 100%; height: 300px; position: relative;">
            <canvas id="finpal-chart-CHART_ID"></canvas>
            <div id="chart-fallback-CHART_ID" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; justify-content: center; align-items: center; background: rgba(255,255,255,0.8);">
                Chart failed to load. Please try again.
            </div>
        </div>
        <script data-chart="true">
            // Direct chart initialization without DOMContentLoaded
            try {
                const chartId = 'finpal-chart-CHART_ID';
                const ctx = document.getElementById(chartId).getContext('2d');
                
                // Create chart with default values
                new Chart(ctx, {
                    type: 'bar',  // Default to bar chart
                    data: {
                        labels: ['Category 1', 'Category 2', 'Category 3'],
                        datasets: [{
                            label: 'Data',
                            data: [300, 200, 100],
                            backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 99, 132, 0.2)'],
                            borderColor: ['rgb(75, 192, 192)', 'rgb(54, 162, 235)', 'rgb(255, 99, 132)'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Chart Title'
                            },
                            legend: {
                                display: true,
                                position: 'bottom'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
                console.log('Chart initialized: ' + chartId);
            } catch (err) {
                console.error('Chart initialization error:', err);
                document.getElementById('chart-fallback-CHART_ID').style.display = 'flex';
            }
        </script>
    </div>
    
    <h3 class="mb-2 mt-4 text-yellow-600 font-semibold">🔍 KEY INSIGHTS</h3>
    <ul class="ml-5 pl-5 list-disc">
        <li>[First key insight from visualization]</li>
        <li>[Second key insight from visualization]</li>
        <li>[Third key insight from visualization]</li>
    </ul>
</div>
```

# FORMAT 6: RECEIPT LISTING
USE WHEN: User wants to see a list of their receipts organized by name, total amount, and category.
```html
<div class="mb-4 p-4 bg-indigo-50 rounded-lg">
    <h3 class="mb-2 text-indigo-600 font-semibold">📋 RECEIPT LIST</h3>
    <p class="ml-5">[Brief summary of the receipts being displayed]</p>
    
    <div class="ml-5 mt-4 overflow-x-auto">
        <table class="min-w-full bg-white border rounded-lg">
            <thead class="bg-indigo-100">
                <tr>
                    <th class="py-2 px-4 border-b text-left">Merchant</th>
                    <th class="py-2 px-4 border-b text-left">Date</th>
                    <th class="py-2 px-4 border-b text-right">Amount</th>
                    <th class="py-2 px-4 border-b text-left">Category</th>
                </tr>
            </thead>
            <tbody>
                <tr class="hover:bg-gray-50">
                    <td class="py-2 px-4 border-b">[Merchant Name (Never the id)]</td>
                    <td class="py-2 px-4 border-b">[Date]</td>
                    <td class="py-2 px-4 border-b text-right">[Amount]</td>
                    <td class="py-2 px-4 border-b">[Category]</td>
                </tr>
                <!-- Repeat for each receipt -->
            </tbody>
            <tfoot class="bg-indigo-50">
                <tr>
                    <td class="py-2 px-4 border-t font-bold" colspan="2">Total</td>
                    <td class="py-2 px-4 border-t text-right font-bold">[Total Amount]</td>
                    <td class="py-2 px-4 border-t"></td>
                </tr>
            </tfoot>
        </table>
    </div>
    
    <h3 class="mb-2 mt-4 text-indigo-600 font-semibold">💡 SUMMARY</h3>
    <ul class="ml-5 pl-5 list-disc">
        <li>Total Receipts: [Number of receipts]</li>
        <li>Most Frequent Category: [Category Name] ([Percentage])</li>
        <li>Largest Transaction: [Merchant Name] - [Amount] ([Date])</li>
    </ul>
</div>
```

RESPONSE SELECTION GUIDELINES:
1. Analyze the user's query for intent (summary, specific question, trend, comparison, visualization, simple query)
2. Consider the available receipt data and its relevance to the query
3. Choose the MOST APPROPRIATE format from the six options above
4. Fill in the template with relevant, accurate information
5. For simple questions that don't need rich formatting, default to FORMAT 5

IMPORTANT:
- Choose only ONE format per response
- NEVER mix multiple formats
- DO NOT explain your choice of format to the user
- NEVER output the format name or selection criteria
- Adapt content within the chosen format to best answer the query
- Keep responses concise (100-300 words total depending on complexity)
- ALWAYS check available receipt context before responding
- For insufficient data, use FORMAT 5 and ask clarifying questions
- When asked for charts or visualizations, ALWAYS use FORMAT 6

DATA VISUALIZATION GUIDELINES:
- Use Chart.js for creating interactive visualizations
- Select appropriate chart types (bar, line, pie, etc.) based on the data
- Always include proper axis labels and titles
- Use meaningful colors that aid understanding
- Include a clear legend when multiple data series are shown
- Provide key insights about what the visualization shows
- NEVER use document.write() in chart scripts as it doesn't work
- ALWAYS set responsive: true in chart options
- ALWAYS give each chart canvas a unique ID if multiple charts are needed
- ALWAYS add data-for attribute to scripts matching the canvas ID

Remember to:
- Focus on TRENDS and PATTERNS rather than exact numbers when appropriate
- Use COMPARATIVE language instead of absolute values when helpful
- Create VISUAL METAPHORS to illustrate financial concepts
- Balance receipt-specific analysis with broader financial wisdom
- Respond directly to what the user is asking about
"""
                    # Add receipt context to the prompt - this is essential!
                    return base_prompt + f"\n\nUSER RECEIPT CONTEXT:\n{receipt_context}"
                
                print("Added FinPal system prompt with HTML formatting, tool sequencing, and conversational guidance")
                
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
    
    # just logs which model being used
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