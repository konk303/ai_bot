# agent/client/agent.py
# Defines the main client agent and its factory for deployment.
# Includes logic for local testing vs. deployment paths for tool integration.
"""Client agent for the Gemini model, combining whole agents."""

import asyncio
from google.adk.agents.llm_agent import LlmAgent # Explicitly import LlmAgent
from contextlib import AsyncExitStack
from google.cloud.aiplatform_v1.types import Content as AiplatformContent, Part as AiplatformPart
from google.adk.tools import agent_tool

# sub-agents
# For local testing, we use the async create_agent from map.agent to get a live map_agent
from map.agent import create_agent as create_live_map_agent
# For deployment, get_map_toolset_for_deployment returns MCPToolset connection parameters
from map.agent import get_map_toolset_for_deployment 
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset 
from google.adk.tools import FunctionTool 

# Make Content and Part globally available in this module for Pydantic schema resolution
Content = AiplatformContent
Part = AiplatformPart

# This function will be run server-side when the deployed agent uses its map tool.
async def invoke_map_tool_dynamically(tool_name: str, tool_input: dict) -> any:
    """
    Dynamically initializes an MCPToolset for map tools using stored connection params,
    invokes a specific tool from that toolset, and returns its result.
    This function is intended to be run on the server side as part of a FunctionTool.
    """
    print(f"invoke_map_tool_dynamically: Called for tool '{tool_name}' with input: {tool_input}")
    
    map_toolset_def = get_map_toolset_for_deployment()
    
    print(f"invoke_map_tool_dynamically: Attempting to get live tools from MCPToolset definition...")
    live_tools, exit_stack = await MCPToolset.from_server(
        connection_params=map_toolset_def.connection_params
    )
    print(f"invoke_map_tool_dynamically: Successfully got {len(live_tools)} live tools.")
    
    async with exit_stack: 
        target_tool = None
        for t in live_tools:
            if t.name == tool_name:
                target_tool = t
                break
        
        if not target_tool:
            print(f"invoke_map_tool_dynamically: Map tool '{tool_name}' not found in live tools.")
            return f"Error: Map tool '{tool_name}' not found."
            
        print(f"invoke_map_tool_dynamically: Found live tool '{target_tool.name}'. Invoking with input: {tool_input}")
        try:
            result = await target_tool(**tool_input) 
            print(f"invoke_map_tool_dynamically: Tool '{tool_name}' result: {result}")
            return result
        except Exception as e:
            print(f"invoke_map_tool_dynamically: Error invoking tool '{tool_name}': {e}")
            return f"Error during map tool '{tool_name}' execution: {str(e)}"


async def create_agent(use_live_map_agent_for_local_test: bool = True):
    """
    Creates the Client LlmAgent.
    - For local testing: uses a live, wrapped map_agent.
    - For deployment: uses a FunctionTool that dynamically invokes map tools.
    """
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()

    client_tools = []
    if use_live_map_agent_for_local_test:
        print("client.create_agent: Creating LIVE map_agent and wrapping with AgentTool for local testing.")
        map_agent_instance, map_agent_exit_stack = await create_live_map_agent()
        await exit_stack.enter_async_context(map_agent_exit_stack) 
        client_tools.append(agent_tool.AgentTool(map_agent_instance))
    else:
        print("client.create_agent: Creating FunctionTool for dynamic map tool invocation for deployment.")
        async def execute_map_operation(tool_name: str, tool_input: dict) -> any:
            """Executes a specific Google Maps operation. Arguments: 'tool_name' (string, e.g., 'maps_geocode', 'maps_directions') and 'tool_input' (dict, the arguments for the specific map tool, e.g., {'address': '1600 Amphitheatre Parkway'} for maps_geocode)."""
            return await invoke_map_tool_dynamically(tool_name, tool_input)

        dynamic_map_tool = FunctionTool(execute_map_operation)
        client_tools.append(dynamic_map_tool)

    client = LlmAgent( # Using the explicit LlmAgent import
        name="client_agent",
        description="(Japanese)Agent to answer questions, with dynamic map tool access for deployment.",
        model="gemini-2.0-flash",
        instruction=(
            "You are a helpful agent. "
            "If the user asks for maps, routes, directions, or place information, use the 'execute_map_operation' tool. "
            "You need to provide the specific 'tool_name' (e.g., 'maps_geocode', 'maps_directions', 'maps_search_places', 'maps_place_details', 'maps_distance_matrix', 'maps_elevation') "
            "and a 'tool_input' dictionary with the arguments for that map tool. "
            "For example, to geocode an address, call execute_map_operation with tool_name='maps_geocode' and tool_input={'address': '1600 Amphitheatre Parkway, Mountain View, CA'}. "
            "For other queries, respond directly."
        ),
        tools=client_tools,
    )
    print(f"client.create_agent: Created client_agent with tools: {client_tools}")
    return client, exit_stack


async def deployment_agent_factory():
    """Async factory function for Vertex AI Agent Engine deployment."""
    print("Running deployment_agent_factory (will include FunctionTool for map tools)...")
    agent_instance, _deployment_exit_stack = await create_agent(use_live_map_agent_for_local_test=False)
    print("Deployment factory returning LlmAgent instance with FunctionTool.")
    return agent_instance
