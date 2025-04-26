#TODO REMOVE FILE RESET API KEYS
import asyncio
import logging
import sys
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

logging.basicConfig(level=logging.DEBUG)

async def main():
    # Test only the brave-search server
    server_params = StdioServerParameters(
        command="node",
        args=[
            "/Users/unrankedalzahrani/Desktop/finpal-svelte/node_modules/@modelcontextprotocol/server-brave-search/dist/index.js"
        ],
        env={"BRAVE_API_KEY": "BSAwdg3KjWBtSceDWb776Vj1MacGMZo"}
    )
    
    print("Starting brave-search server test...")
    try:
        # Set a timeout for the entire operation
        async with asyncio.timeout(30):
            # Initialize session using the correct pattern
            async with stdio_client(server_params) as (reader, writer):
                client = ClientSession(reader, writer)
                await client.initialize()
                print("Session initialized successfully")
                
                # List tools
                tools_result = await client.list_tools()
                print(f"Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f" - {tool.name}: {tool.description}")
                
                # Test search if tools are available
                if tools_result.tools:
                    search_tool = next((t for t in tools_result.tools if "search" in t.name.lower()), None)
                    if search_tool:
                        print(f"\nTesting search with '{search_tool.name}'")
                        result = await client.call_tool(
                            search_tool.name, 
                            arguments={"search_term": "What is the weather in New York?"}
                        )
                        print(f"Search result: {result[:500]}...(truncated)" if result and len(result) > 500 else result)
        
        print("Session closed successfully")
        
    except asyncio.TimeoutError:
        print("Operation timed out after 30 seconds")
        sys.exit(1)
    except Exception as e:
        print(f"Error in brave-search test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1) 