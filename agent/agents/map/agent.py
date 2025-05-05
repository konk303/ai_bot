import asyncio
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

async def create_agent():
    """Get tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",
                  "@modelcontextprotocol/server-google-maps",
                  ],
            # Pass the API key as an environment variable to the npx process
            env={
                "GOOGLE_MAPS_API_KEY": "AIzaSyBPp599jTEL1UrnG27jrISS5F4pNWwxvKQ"
            }
        )
    )

    print(f"--- Connected to map-mcp. Discovered {len(tools)} tool(s). ---")
    for tool in tools:
        print(f"  - Discovered tool: {tool.name}")

    agent = LlmAgent(
        model='gemini-2.0-flash',  # Adjust if needed
        name='maps_assistant',
        instruction='Help user with mapping and directions using available tools.',
        tools=tools,
    )

    return agent, exit_stack

root_agent = create_agent()
