import asyncio
import sys
from src.services.pydantic_mcp_agent import get_pydantic_ai_agent

async def main():
    print("Testing MCP agent creation...")
    client, agent = await get_pydantic_ai_agent()
    
    if client is None:
        print("ERROR: MCP client is None")
    else:
        print(f"MCP client initialized: {client}")
    
    if agent is None:
        print("ERROR: Agent is None")
    else:
        print(f"Agent initialized: {agent}")
        
    if hasattr(agent, 'tools'):
        print(f"Agent has {len(agent.tools)} tools:")
        for tool in agent.tools:
            print(f"  - {tool.name}")
    else:
        print("Agent has no tools attribute")
    
    print("Test complete")

if __name__ == "__main__":
    asyncio.run(main()) 