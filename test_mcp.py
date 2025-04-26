
#TODO REMOVE FILE RESET API KEYS
import asyncio
import json
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

async def main():
    # Test filesystem server
    print("Testing filesystem server...")
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/unrankedalzahrani/Desktop/finpal-svelte"],
    )
    try:
        async with stdio_client(server_params) as (reader, writer):
            client = ClientSession(reader, writer)
            await client.initialize()
            tools = await client.list_tools()
            print(f"Found {len(tools.tools)} tools in filesystem server")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error with filesystem server: {e}")

    # Test brave-search server
    print("\nTesting brave-search server...")
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": "BSAwdg3KjWBtSceDWb776Vj1MacGMZo"}
    )
    try:
        async with stdio_client(server_params) as (reader, writer):
            client = ClientSession(reader, writer)
            await client.initialize()
            tools = await client.list_tools()
            print(f"Found {len(tools.tools)} tools in brave-search server")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error with brave-search server: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 