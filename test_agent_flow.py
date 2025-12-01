import os
import sys
from power_analysis_agent import create_power_analysis_agent

import asyncio

async def test_agent_flow():
    print("Testing Agent Flow...")
    
    # Use a dummy model name for testing flow logic (ADK might try to init it, but we are testing tool mainly)
    model_name = "gemini-1.5-pro-002"

    agent = create_power_analysis_agent(model_name)
    
    # Test case: User asks for power analysis
    user_query = "I need to calculate sample size for a t-test with effect size 0.5 and power 0.8."
    print(f"\nUser Query: {user_query}")
    
    # In a real scenario, the model would generate a tool call.
    # Here, we can manually test the tool if we are using a mock, 
    # or rely on the ADK's loop if using a real model.
    
    # Let's directly test the tool via the agent's tool list to ensure integration is correct
    tool = agent.tools[0]
    print(f"Found Tool: {tool.name}")
    
    # Execute tool manually to verify integration
    print("Executing tool manually with params: test_type='t.test', effect_size=0.5, power=0.8, alpha=0.05")
    result = tool.func(test_type='t.test', effect_size=0.5, power=0.8, alpha=0.05)
    print(f"Tool Result:\n{result}")
    
    if "n = 63.76561" in result:
        print("PASS: Tool execution successful")
    else:
        print("FAIL: Tool execution failed")

    # Test agent.run_live - SKIPPED
    # run_live requires real model interaction and credentials which may not be available in CI/Test env.
    # The tool execution above verifies the core logic.
    print("\nSkipping agent.run_live() test (requires live model credentials).")

if __name__ == "__main__":
    asyncio.run(test_agent_flow())
