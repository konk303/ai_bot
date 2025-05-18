# agent.py (modify get_tools_async and other parts as needed)

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


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
                "GOOGLE_MAPS_API_KEY": API_KEY,
            }
        )
    )

    agent = LlmAgent(
        model='gemini-2.0-flash', # Adjust if needed
        name='maps_assistant',
        instruction='Help user with mapping and directions using available tools.',
        tools=tools,
    )
    return agent, exit_stack

root_agent = create_agent()
