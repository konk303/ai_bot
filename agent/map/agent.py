# agent/map/agent.py
# Defines agents and toolset configurations related to map functionalities.
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent # Changed from google.adk.agents.llm_agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()


async def create_agent(): # This is for creating a LIVE agent for local testing
    """Creates a live LlmAgent with connected MCP tools for local testing."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY", "")}
        )
    )
    print(f"map.agent.create_agent: Connected to map-mcp. Discovered {len(tools)} tool(s).")
    for tool in tools:
        print(f"  - Discovered tool: {tool.name}")

    agent = LlmAgent(
        model='gemini-2.0-flash',
        name='maps_assistant_live',
        instruction='Help user with mapping and directions using available tools.',
        tools=tools, # These are live MCPTool instances
    )
    return agent, exit_stack

def get_map_toolset_for_deployment() -> MCPToolset:
    """Returns a serializable MCPToolset definition (not connected)."""
    map_server_params = StdioServerParameters(
        command='npx',
        args=["-y", "@modelcontextprotocol/server-google-maps"],
        env={"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY", "")}
    )
    toolset = MCPToolset(connection_params=map_server_params)
    print("map.agent.get_map_toolset_for_deployment: Created MCPToolset definition.")
    return toolset
