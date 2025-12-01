from google.adk import Agent
import sys

agent = Agent(name="test", model="gemini-1.5-pro-002")
with open("agent_dir.txt", "w") as f:
    f.write(str(dir(agent)))
