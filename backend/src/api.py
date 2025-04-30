# test 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys
import pathlib
import logging
import json
from dotenv import load_dotenv
import time
import re
import traceback
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import google.generativeai with proper error handling
try:
    import google.generativeai as genai
    has_genai = True
    
    # Initialize Gemini API for direct context endpoint
    try:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("No Google API key found. Direct chat endpoint will not work")
            has_genai = False
        else:
            genai.configure(api_key=api_key)
            logger.info("Gemini API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {str(e)}")
        has_genai = False
except ImportError:
    logger.error("google-generativeai package not installed. Direct chat endpoint will not work.")
    logger.error("Install with: pip install google-generativeai")
    has_genai = False
    genai = None

# Ensure our services directory is in the path
current_dir = pathlib.Path(__file__).parent.absolute()
services_dir = os.path.join(current_dir, "services")
sys.path.insert(0, str(services_dir))

# Import our services
try:
    from src.services.pydantic_mcp_agent import get_pydantic_ai_agent
except ImportError:
    logger.error("Failed to import pydantic_mcp_agent")
    get_pydantic_ai_agent = None

try:
    from src.services.direct_context import fetch_receipt_context
except ImportError:
    logger.error("Failed to import direct_context")
    fetch_receipt_context = None

# Create a new FastAPI app (this is our web server)
app = FastAPI()

# Allow requests from our frontend (CORS settings)
# Without this, the browser would block requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, change to your frontend URL only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store our AI agent globally so we don't create a new one for each request
# This makes responses faster and maintains conversation context
global_mcp_client = None
global_agent = None
messages_history = []
MAX_HISTORY_LENGTH = 20  # Maximum number of message pairs to keep in history

# Function to limit message history size
def limit_message_history():
    global messages_history
    # If message history is getting too long, trim it
    # Keep only the most recent MAX_HISTORY_LENGTH messages
    if len(messages_history) > MAX_HISTORY_LENGTH * 2:  # Each exchange has 2 messages (user & assistant)
        print(f"Trimming message history from {len(messages_history)} to {MAX_HISTORY_LENGTH * 2} messages")
        messages_history = messages_history[-MAX_HISTORY_LENGTH * 2:]

# Helper function: Get existing agent or create a new one if needed
async def get_or_create_agent():
    global global_mcp_client, global_agent
    if global_agent is None:
        # This calls the function from pydantic_mcp_agent.py that sets up the AI
        # It returns both the MCP client and the agent
        global_mcp_client, global_agent = await get_pydantic_ai_agent()
    return global_agent

# ENDPOINT 1: Health check
# Frontend uses this to check if the backend is running
@app.get("/api/health")
async def health():
    try:
        agent = await get_or_create_agent()
        # Determine environment
        is_render = os.environ.get("RENDER") == "true" or os.environ.get("IS_RENDER") == "true"
        env_type = "production" if is_render else "local"
        hostname = os.environ.get("HOSTNAME", "unknown")
        
        # Always return connected: true if we have an agent, regardless of tools
        return {
            "status": "ok", 
            "connected": True,
            "environment": env_type,
            "hostname": hostname,
            "timestamp": datetime.now().isoformat(),
            "tools_available": len(agent.tools) if hasattr(agent, 'tools') else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "connected": False, "environment": "unknown"}

# ENDPOINT 2: Connect to AI service
# Frontend calls this when initializing
@app.post("/api/connect")
async def connect():
    try:
        # Initialize the AI agent with MCP tools
        agent = await get_or_create_agent()
        
        # Always return a valid response even if agent has no tools
        return {
            "status": "connected", 
            "tools": [] if not hasattr(agent, 'tools') or not agent.tools else [{"name": tool.name} for tool in agent.tools]
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR IN /api/connect: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINT 3: Get available tools 
@app.get("/api/tools")
async def get_tools():
    try:
        agent = await get_or_create_agent()
        tool_info = []
        if hasattr(agent, 'tools'):
            tool_info = [{"name": tool.name} for tool in agent.tools]
        return {"tools": tool_info}
    except Exception as e:
        return {"error": str(e), "tools": []}

# Define the expected format for chat messages coming from frontend
class ChatMessage(BaseModel):
    message: str  # Each message will have a "message" field with the user's text

# ENDPOINT 4: Process chat messages
# This is the main endpoint that handles user messages
@app.post("/api/chat")
async def chat(message: ChatMessage):
    global messages_history
    
    try:
        # Get our AI agent
        agent = await get_or_create_agent()
        
        # Log the request
        print(f"Processing chat request: {message.message}")
        
        # Process the message with the AI agent
        # We pass message_history so the AI remembers previous conversation
        start_time = time.time()
        result = await agent.run(message.message, message_history=messages_history)
        processing_time = time.time() - start_time
        print(f"Agent processed message in {processing_time:.2f} seconds")
        
        # Safely save conversation history - handle case if all_messages() doesn't exist
        try:
            if hasattr(result, 'all_messages') and callable(result.all_messages):
                messages_history.extend(result.all_messages())
                #todo remove if needed. Limit history size to prevent token accumulation
                limit_message_history()
        except Exception as history_error:
            print(f"Warning: Could not save message history: {history_error}")
        
        # Get the response content from the result
        # The AgentRunResult object from pydantic-ai has the response in data
        response_text = ""
        
        # Check the structure of the result to determine how to extract the response
        if hasattr(result, 'data'):
            response_text = result.data
        elif hasattr(result, 'text'):
            response_text = result.text
        elif hasattr(result, 'content'):
            response_text = result.content
        elif hasattr(result, 'response'):
            response_text = result.response
        else:
            # Fallback to string representation
            print(f"Couldn't extract text directly. Result object: {result}")
            response_text = str(result)
        
        # Clean up the response to remove any markdown code fences
        if isinstance(response_text, str):
            # Remove markdown code fences if present
            if response_text.startswith("```html"):
                response_text = response_text.replace("```html", "", 1)
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
            
            # Remove any other code fence markers
            response_text = response_text.replace("```", "")
            
            # Check if there's tool command at the beginning
            has_leading_tool_code = False
            tool_command_patterns = [
                r'^tool_code',
                r'^sequential_thinking\.think',
                r'^sequential_thinking\.run',
                r'^memory_tool\.',
                r'^brave_search\.search_and_summarize',
                r'^print\(brave_search\.',
                r'^brave_search\.',
                r'^google_maps\.',
                r'^yfinance\.'
            ]
            
            for pattern in tool_command_patterns:
                if re.search(pattern, response_text.strip(), re.DOTALL):
                    has_leading_tool_code = True
                    break
            
            # If there's tool code and no HTML response yet, try to extract an actual answer
            if has_leading_tool_code and not response_text.strip().endswith(">"):
                print("Tool command detected, extracting answer and preserving thinking")
                
                # Try to extract the result from sequential thinking
                thinking_result_match = re.search(r'"result":\s*"(.+?)"', response_text, re.DOTALL)
                
                # Format this nicely to have both thinking and content
                if thinking_result_match:
                    # Extract the actual content from the sequential thinking result
                    extracted_content = thinking_result_match.group(1)
                    extracted_content = extracted_content.replace('\\n', '\n').replace('\\"', '"')
                    
                    # Create a clear HTML response with the extracted content
                    html_response = f'<div class="p-4 bg-gray-50 rounded-lg"><p class="text-lg">{extracted_content}</p></div>'
                    
                    # Return both thinking and content - frontend will handle the UI
                    response_text = response_text + "\n\n" + html_response
                else:
                    # Try to find any human-readable text after the tool commands
                    normal_text_match = re.search(r'\)\s*\n+([\s\S]+)', response_text)
                    if normal_text_match:
                        text_content = normal_text_match.group(1).strip()
                        html_response = f'<div class="p-4 bg-gray-50 rounded-lg"><p class="text-lg">{text_content}</p></div>'
                        response_text = response_text + "\n\n" + html_response
                    else:
                        # If we can't extract anything useful, add a generic response
                        html_response = '<div class="p-4 bg-gray-50 rounded-lg"><p class="text-lg">I\'ve analyzed your question. Please check my thought process for details.</p></div>'
                        response_text = response_text + "\n\n" + html_response
                
                # Clean up any Python escaping
                response_text = re.sub(r'\\n', '\n', response_text)
                response_text = re.sub(r'\\"', '"', response_text)
            
            # Trim whitespace
            response_text = response_text.strip()
            
            # Log the final response length
            print(f"Final response length: {len(response_text)} characters")
        
        # Return the AI's response to the frontend
        return {"response": response_text}
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Log the error for debugging
        return {"response": f"Sorry, an error occurred: {str(e)}"}

# ENDPOINT: Reset conversation
# This lets the frontend reset the conversation if needed
@app.post("/api/reset")
async def reset_conversation():
    global messages_history
    
    try:
        old_length = len(messages_history)
        messages_history = []
        return {
            "status": "success", 
            "message": f"Conversation reset. Cleared {old_length} messages from history."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to reset conversation: {str(e)}"}

# #todo comment extra (dont remove) function Define request model for direct chat
# class DirectChatMessage(BaseModel):
#     message: str
#     model: str = "gemini-2.5-pro"  # Default model, can be overridden

# # ENDPOINT 5: Direct context chat using raw receipt data
# # This endpoint provides a direct way to query receipt data with simpler caching
# @app.post("/api/direct_chat")
# async def direct_chat(message: DirectChatMessage):
#     try:
#         # Check if we can fetch receipt context
#         if fetch_receipt_context is None:
#             return {
#                 "response": "Direct chat is currently unavailable. The receipt context service is not available."
#             }
        
#         # Get the agent for formatting consistency
#         agent = await get_or_create_agent()
#         if agent is None:
#             return {
#                 "response": "Direct chat is currently unavailable. Agent initialization failed."
#             }

#         # Fetch raw receipt data from Firestore (will use cache if available)
#         receipt_context = fetch_receipt_context(limit=300)
        
#         # Get the agent's system prompt instead of creating a custom one
#         # This ensures the same formatting and style is used across all endpoints
#         system_prompt = ""
#         if hasattr(agent, 'system_prompt_func'):
#             system_prompt = agent.system_prompt_func()
#         else:
#             # Fallback system instruction if system_prompt_func isn't available
#             system_prompt = """
#             You are FinPal, a Saudi-focused financial assistant providing personalized insights based on receipt analysis.
#             NEVER show raw tool commands in your response.
#             Format your responses with INSIGHT, RECOMMENDATIONS, BREAKDOWN, and NEXT STEPS sections.
#             """
        
#         # Build prompt with system prompt and receipt context
#         prompt = f"Using the following system instructions: {system_prompt}\n\nReceipt data: {receipt_context}\n\nUser question: {message.message}"
        
#         # Use the pydantic agent for consistent formatting
#         result = await agent.run(prompt)
        
#         # Extract response from result
#         response_text = ""
#         if hasattr(result, 'data'):
#             response_text = result.data
#         elif hasattr(result, 'text'):
#             response_text = result.text
#         elif hasattr(result, 'content'):
#             response_text = result.content
#         elif hasattr(result, 'response'):
#             response_text = result.response
#         else:
#             print(f"Couldn't extract text directly. Result object: {result}")
#             response_text = str(result)
        
#         # Clean up response
#         if isinstance(response_text, str):
#             # Remove tool command artifacts if they managed to slip through
#             if "tool_code" in response_text or "sequential_thinking.run" in response_text:
#                 response_text = "I'm analyzing your receipts to provide insights. Please ask me a specific question about your spending or receipts."
            
#             # Remove markdown code fences
#             if response_text.startswith("```html"):
#                 response_text = response_text.replace("```html", "", 1)
#                 if response_text.endswith("```"):
#                     response_text = response_text[:-3]
            
#             response_text = response_text.replace("```", "").strip()
        
#         return {"response": response_text}
        
#     except Exception as e:
#         logger.error(f"Error in direct chat: {str(e)}")
#         return {"response": f"Sorry, an error occurred: {str(e)}"}

# Cleanup handler for when the server shuts down
@app.on_event("shutdown")
async def shutdown_event():
    global global_mcp_client
    if global_mcp_client is not None:
        try:
            await global_mcp_client.cleanup()
            print("MCP client resources cleaned up")
        except Exception as e:
            print(f"Error cleaning up MCP client: {e}") 