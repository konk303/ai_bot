"""Client agent for the Gemini model, combining whole agents."""

from google.adk.tools import agent_tool
from google.adk.agents import Agent
from contextlib import AsyncExitStack

# sub-agents
from map.agent import create_agent as create_map_agent
# from gdrive.agent import create_agent as create_gdrive_agent
from google_search.agent import root_agent as google_search_agent

async def create_agent(dummy: bool = False):
    """Create the Client agent that delegates to sub-agents."""
    # Manage multiple exit stacks for async sub-agents
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()

    # Instantiate gdrive (async) and enter its exit stack
    map_agent, map_stack = await create_map_agent()
    await exit_stack.enter_async_context(map_stack)

    tools = [
            agent_tool.AgentTool(google_search_agent),
            # agent_tool.AgentTool(agent=map_agent)
        ]
    if not dummy:
        tools.extend(
            [
                agent_tool.AgentTool(agent=map_agent)
            ]
        )


    # Create the Coordinator agent
    agent = Agent(
        name="root_agent",
        description="(Japanese)Agent to answer questions about anything, combining other agents",
        model="gemini-2.5-flash-preview-04-17",
        instruction=(
            "You are a helpful agent who can answer user questions about anything."
            "\n1. When the user asks for maps/routes/directions, delegate to Map and return its raw list."
            "\n2. When the user asks for gdrive files, delegate to Gdrive and return its raw list."
            "\n3. When the user asks for real time events, delegate to google_search and return its raw list."
            "\n4. For other queries, respond directly without delegation."
        ),
        tools=tools
    )

    return agent, exit_stack
