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
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
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
        # loop over servers and initialize them
        for server in self.servers:
            try:
                await server.initialize() # init server
                tools = await server.create_pydantic_ai_tools() # create pydantic tools
                self.tools += tools # add tools to list
            except Exception as e:
                logging.error(f"Failed to initialize server: {e}")
                await self.cleanup_servers()
                return []

        return self.tools

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        for server in self.servers:
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"Warning during cleanup of server {server.name}: {e}")

    async def cleanup(self) -> None:
        """Clean up all resources including the exit stack."""
        try:
            # First clean up all servers
            await self.cleanup_servers()
            # Then close the exit stack
            await self.exit_stack.aclose()
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
        command = (
            shutil.which("npx") #or docker depends on server
            if self.config["command"] == "npx"
            else self.config["command"]
        )
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")
        #next is identifying the parameters of the server
        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"], #mcp configs
            env=self.config["env"] # for api keys
            if self.config.get("env")
            else None,
        )
        try:
            #Make the connection to the server via stdio
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport #read and write to the server
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize() # finally initialize the session
            self.session = session #store the *session*
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    # take the tools from the server and convert them to pydantic_ai Tools
    async def create_pydantic_ai_tools(self) -> List[PydanticTool]: 
        """Convert MCP tools to pydantic_ai Tools."""
        tools = (await self.session.list_tools()).tools #get list of tools
        return [self.create_tool_instance(tool) for tool in tools] #convert each tool to a pydantic_ai Tool

# actual excute the tool
    def create_tool_instance(self, tool: MCPTool) -> PydanticTool:#we take mcp tool -> pydantic tool
        """Initialize a Pydantic AI Tool from an MCP Tool."""
        async def execute_tool(**kwargs: Any) -> Any:
            return await self.session.call_tool(tool.name, arguments=kwargs)

        async def prepare_tool(ctx: RunContext, tool_def: ToolDefinition) -> ToolDefinition | None:
            tool_def.parameters_json_schema = tool.inputSchema #input schema for parameters to know query
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
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")  