"""Client agent for the Gemini model, combining whole agents."""
from google.adk.tools import agent_tool
from google.adk.agents import Agent
from map.agent import root_agent as map_agent
from google_search.agent import root_agent as google_search_agent
MODEL = "gemini-2.0-flash"


tools = [
    agent_tool.AgentTool(agent=google_search_agent),
    agent_tool.AgentTool(agent=map_agent)
]

root_agent = Agent(
    name="root_agent",
    description="(Japanese)Agent to answer questions about anything, combining other tools/agents",
    model=MODEL,
    instruction=(
        "You are a helpful agent who can answer user questions about anything."
        "\n1. When the user asks for real time informations, delegate to google_search"
        "\n2. When the user asks for maps/routes/directions, delegate to Map"
        "\n3. For other queries, respond directly without delegation."
    ),
    tools=tools
)
