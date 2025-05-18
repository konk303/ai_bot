# agent/gdrive/agent.py
# Defines agents and toolset configurations related to gdrive functionalities.
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def create_agent():
    """Get tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                  "@modelcontextprotocol/server-gdrive"
                  ],
            env={"GDRIVE_CREDENTIALS_PATH": "/tmp/.gdrive-server-credentials.json"},
        )
    )

    agent = LlmAgent(
        model='gemini-2.0-flash',
        name='gdrive_assistant',
        instruction=(
            '(Japanese)Help user accessing the google drive documents and files. '
        ),
        tools=tools,
     )
    return agent, exit_stack


root_agent = create_agent()
