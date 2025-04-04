# test
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from src.services.pydantic_mcp_agent import get_pydantic_ai_agent
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
        # Always return connected: true if we have an agent, regardless of tools
        return {"status": "ok", "connected": True}
    except Exception as e:
        return {"status": "error", "message": str(e), "connected": False}

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
        
        # Process the message with the AI agent
        # We pass message_history so the AI remembers previous conversation
        result = await agent.run(message.message, message_history=messages_history)
        
        # Safely save conversation history - handle case if all_messages() doesn't exist
        try:
            if hasattr(result, 'all_messages') and callable(result.all_messages):
                messages_history.extend(result.all_messages())
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
        
        # Return the AI's response to the frontend
        return {"response": response_text}
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Log the error for debugging
        return {"response": f"Sorry, an error occurred: {str(e)}"}

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