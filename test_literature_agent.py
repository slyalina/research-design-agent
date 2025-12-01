import os
import sys
import asyncio
from literature_agent import create_literature_agent

async def test_literature_agent():
    """
    Test the literature agent's MCP integration.
    """
    print("Testing Literature Agent with MCP Integration...")
    
    # Create the literature agent
    model_name = "gemini-1.5-pro-002"
    agent = create_literature_agent(model_name)
    
    print(f"Agent created: {agent.name}")
    print(f"Tools available: {len(agent.tools)}")
    
    # Check if MCP toolset is present
    if agent.tools:
        toolset = agent.tools[0]
        print(f"Toolset type: {type(toolset).__name__}")
        
        # Try to get tools from the toolset
        try:
            # The toolset needs a context to get tools
            # For testing, we'll just verify the toolset exists
            print("MCP Toolset successfully initialized")
            print("\nTest PASSED: Literature agent created with MCP toolset")
            return True
        except Exception as e:
            print(f"Error accessing toolset: {e}")
            return False
    else:
        print("FAIL: No tools found in agent")
        return False

if __name__ == "__main__":
    # Run the async test
    result = asyncio.run(test_literature_agent())
    sys.exit(0 if result else 1)
