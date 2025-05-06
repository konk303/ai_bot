"""Client agent for the Gemini model, combining whole agents."""

from google.adk.agents import Agent
from contextlib import AsyncExitStack
from google.adk.tools import agent_tool

# sub-agents
from map.agent import create_agent as create_map_agent

async def create_agent():
    """Creates the Client agent that delegates to sub-agents."""
    # Manage multiple exit stacks for async sub-agents
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()

    # Instantiate map (async) and enter its exit stack
    map_agent, map_stack = await create_map_agent()
    await exit_stack.enter_async_context(map_stack)

    # Create the Coordinator agent
    client = Agent(
        name="client_agent",
        description="(Japanese)Agent to answer questions about anything, combining other agents",
        model="gemini-2.5-flash-preview-04-17",
        instruction=(
            "You are a helpful agent who can answer user questions about anything."
            "\n1. When the user asks for maps/routes/directions, delegate to Map and return its raw list."
            "\n2. For other queries, respond directly without delegation."
        ),
        # sub_agents=[map_agent]
        tools=[agent_tool.AgentTool(map_agent)],
    )

    return client, exit_stack

root_agent = create_agent()
