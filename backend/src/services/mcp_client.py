from pydantic_ai import RunContext, Tool as PydanticTool
from pydantic_ai.tools import ToolDefinition
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool
from contextlib import AsyncExitStack
from typing import Any, List
import asyncio
import logging
import shutil
import json
import os
import sys
import pathlib

# Add the backend directory to the Python path to fix imports
current_dir = pathlib.Path(__file__).parent.resolve()
backend_dir = current_dir.parent.parent
sys.path.insert(0, str(backend_dir))

# basic logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
# the class or local excuter of all MCP servers
class MCPClient:
    """Manages connections to one or more MCP servers based on mcp_config.json"""

    def __init__(self) -> None:
        self.servers: List[MCPServer] = [] # create a list of servers from MCPSERVER class
        self.config: dict[str, Any] = {} # the configurations
        self.tools: List[Any] = [] # list of tools
        self.exit_stack = AsyncExitStack() # exit stack

    def load_servers(self, config_path: str) -> None:
        """Load server configuration from a JSON file (typically mcp_config.json)
        and creates an instance of each server (no active connection until 'start' though).
        """
        with open(config_path, "r") as config_file:
            self.config = json.load(config_file)
        #for each server get name and config (ex: brave-search, config mcpservers)
        self.servers = [MCPServer(name, config) for name, config in self.config["mcpServers"].items()]

    # the function to start the servers "START"
    async def start(self) -> List[PydanticTool]:
        """START each MCP server and returns the tools for each server formatted for Pydantic AI."""
        self.tools = []
        
        # Get priority levels from config
        priorities = self.config.get("serverPriorities", {})
        essential_servers = set(priorities.get("essential", []))
        
        # First, initialize only essential servers and those with autostart=true
        for server in self.servers:
            # Check if server is essential either by name or by priority setting
            is_essential = (server.name in essential_servers or 
                            server.config.get("priority") == "essential")
            
            # Initialize if essential or has autostart=true
            if not (is_essential or server.config.get("autostart", False)):
                logging.info(f"Skipping non-essential server: {server.name} - Priority: {server.config.get('priority', 'unknown')}, Autostart: {server.config.get('autostart', False)}")
                continue
                
            try:
                logging.info(f"Initializing server: {server.name} - Priority: {server.config.get('priority', 'unknown')}, Autostart: {server.config.get('autostart', False)}")
                await server.initialize() # init server
                logging.debug(f"Creating pydantic tools for server: {server.name}")
                tools = await server.create_pydantic_ai_tools() # create pydantic tools
                logging.debug(f"Found {len(tools)} tools in server: {server.name}")
                for tool in tools:
                    logging.debug(f"  - {tool.name}")
                self.tools += tools # add tools to list
            except Exception as e:
                logging.error(f"Failed to initialize server {server.name}: {e}")
                logging.error(f"Error details: {type(e).__name__}: {e}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
                # Continue with other servers instead of exiting early
                # Just clean up the failed server
                try:
                    await server.cleanup()
                except Exception as cleanup_error:
                    logging.error(f"Error cleaning up failed server {server.name}: {cleanup_error}")

        # Only call cleanup_servers if we couldn't initialize any servers
        if not self.tools:
            logging.warning("No tools were found from any servers")
            
        return self.tools

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        for server in self.servers:
            try:
                await server.cleanup()
            except (asyncio.CancelledError, Exception) as e:
                logging.warning(f"Warning during cleanup of server {server.name}: {e}")
                # Don't propagate the CancelledError, as we're already cleaning up

    async def cleanup(self) -> None:
        """Clean up all resources including the exit stack."""
        try:
            # First clean up all servers
            await self.cleanup_servers()
            # Then close the exit stack
            try:
                await self.exit_stack.aclose()
            except (asyncio.CancelledError, Exception) as e:
                logging.warning(f"Warning during exit stack cleanup: {e}")
        except Exception as e:
            logging.warning(f"Warning during final cleanup: {e}")


class MCPServer: #CLASS FOR EACH MCP SERVER
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: dict[str, Any]) -> None: 
        self.name: str = name #SERVER NAME
        self.config: dict[str, Any] = config #SERVER CONFIG
        self.stdio_context: Any | None = None #STDIO CONTEXT (server connection)
        self.session: ClientSession | None = None #Store Connection of client
        self._cleanup_lock: asyncio.Lock = asyncio.Lock() #CLEANUP LOCK
        self.exit_stack: AsyncExitStack = AsyncExitStack() #EXIT STACK

    async def initialize(self) -> None:
        """Initialize the server connection."""
        try:
            command = (
                shutil.which("npx") #or docker depends on server
                if self.config["command"] == "npx"
                else self.config["command"]
            )
            if command is None:
                raise ValueError(f"The command '{self.config['command']}' could not be found in PATH. Make sure it's installed.")
            
            # Check if the module exists before attempting to run it
            if self.config["command"] == "node":
                module_path = self.config["args"][0]
                if not os.path.exists(module_path):
                    logging.warning(f"Module not found at {module_path} for server {self.name}")
                    logging.warning(f"Skipping server {self.name}")
                    return
            
            #next is identifying the parameters of the server
            server_params = StdioServerParameters(
                command=command,
                args=self.config["args"], #mcp configs
                env=self.config["env"] # for api keys
                if self.config.get("env")
                else None,
            )
            
            logging.debug(f"Starting MCP server: {self.name} with command: {command} {' '.join(self.config['args'])}")
            
            #Make the connection to the server via stdio
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport #read and write to the server
            
            logging.debug(f"Server {self.name} stdio connection established, creating session")
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logging.debug(f"Initializing session for server: {self.name}")
            await session.initialize() # finally initialize the session
            self.session = session #store the *session*
            logging.debug(f"Server {self.name} initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            await self.cleanup()
            # Instead of raising the exception, just return
            # This allows other servers to continue working
            return

    # take the tools from the server and convert them to pydantic_ai Tools
    async def create_pydantic_ai_tools(self) -> List[PydanticTool]: 
        """Convert MCP tools to pydantic_ai Tools."""
        try:
            # If session wasn't initialized properly, return empty list
            if not self.session:
                logging.warning(f"Session for server {self.name} not initialized, skipping tool creation")
                return []
                
            tools = (await self.session.list_tools()).tools #get list of tools
            return [self.create_tool_instance(tool) for tool in tools] #convert each tool to a pydantic_ai Tool
        except Exception as e:
            logging.error(f"Error listing tools for server {self.name}: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            # Return empty list if we can't get tools
            return []

# actual excute the tool
    def create_tool_instance(self, tool: MCPTool) -> PydanticTool:#we take mcp tool -> pydantic tool
        """Initialize a Pydantic AI Tool from an MCP Tool."""
        async def execute_tool(**kwargs: Any) -> Any:
            return await self.session.call_tool(tool.name, arguments=kwargs)

        async def prepare_tool(ctx: RunContext, tool_def: ToolDefinition) -> ToolDefinition | None:
            # Make sure the input schema has the proper format for pydantic-ai
            input_schema = tool.inputSchema.copy()
            
            # Add type if missing
            if 'type' not in input_schema:
                input_schema['type'] = 'object'
                
            # Remove $schema field if present
            if '$schema' in input_schema:
                del input_schema['$schema']
                
            # Clean properties
            if 'properties' in input_schema:
                for prop in input_schema['properties'].values():
                    if isinstance(prop, dict) and '$schema' in prop:
                        del prop['$schema']
            
            # Set the cleaned schema
            tool_def.parameters_json_schema = input_schema
            return tool_def
            
        # tool attributes
        return PydanticTool(
            execute_tool,
            name=tool.name,
            description=tool.description or "",
            takes_ctx=False,
            prepare=prepare_tool
        )

    #Clean up the server
    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                try:
                    await self.exit_stack.aclose()
                except (asyncio.CancelledError, Exception) as e:
                    logging.warning(f"Warning while closing exit stack for server {self.name}: {e}")
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")  