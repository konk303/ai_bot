# agent/deploy.py
# Main script for deploying the agent to Vertex AI Agent Engines.
# Includes local testing and create/update deployment logic.
import asyncio
import os
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from client.agent import create_agent, deployment_agent_factory # Updated import
from contextlib import AsyncExitStack # Added for AdkApp resource management

DISPLAY_NAME = "gemini_agent"

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = "gs://ai-agent-staging" # Ensure this bucket exists and is accessible

async def main():
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    # Local testing with AdkApp
    print("--- Local AdkApp Test ---")
    local_test_agent, local_test_exit_stack = await create_agent()
    async with local_test_exit_stack: 
        app = reasoning_engines.AdkApp(
            agent=local_test_agent,
            enable_tracing=True,
        )
        print("Streaming query to local AdkApp...")
        for event in app.stream_query(
            user_id="u_123_local",
            message="hello, how are you locally?",
        ):
            print(f"Local event: {event}")
        print("Local AdkApp test finished.")
    print("--- End Local AdkApp Test ---")

    # Deployment to Vertex AI Agent Engines
    print("\n--- Vertex AI Agent Engine Deployment ---")

    all_remote_apps_with_name = list(agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"'))
    if len(all_remote_apps_with_name) > 1:
        print(f"Found {len(all_remote_apps_with_name)} agent engines with display name '{DISPLAY_NAME}'. Deleting all but the first one found...")
        for i, app_to_delete in enumerate(all_remote_apps_with_name):
            if i > 0: 
                print(f"Deleting extra agent engine: {app_to_delete.resource_name}")
                try:
                    app_to_delete.delete(force=True)
                    print(f"Successfully deleted extra agent: {app_to_delete.resource_name}")
                except Exception as e:
                    print(f"Error deleting extra agent {app_to_delete.resource_name}: {e}")
        remote_apps = list(agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"'))
    else:
        remote_apps = all_remote_apps_with_name

    print("Awaiting deployment_agent_factory to get agent instance for deployment...")
    agent_instance_for_deployment = await deployment_agent_factory()
    print(f"Agent instance for deployment: {type(agent_instance_for_deployment)}")

    if not remote_apps:
        print(f"No agent engine found with display name '{DISPLAY_NAME}'. Creating new one...")
        remote_app = agent_engines.create(
            display_name=DISPLAY_NAME,
            agent_engine=agent_instance_for_deployment,
            requirements=["google-cloud-aiplatform[adk,agent_engines]"],
            extra_packages=["client", "map"],
            description="Gemini Agent for various tasks.",
        )
        print(f"Successfully created new agent engine: {remote_app.resource_name}")
    else:
        print(f"Found existing agent engine with display name '{DISPLAY_NAME}'. Updating...")
        existing_remote_app = remote_apps[0]
        remote_app = existing_remote_app.update(
            agent_engine=agent_instance_for_deployment,
            requirements=["google-cloud-aiplatform[adk,agent_engines]"],
            extra_packages=["client", "map"]
        )
        print(f"Successfully updated existing agent engine: {remote_app.resource_name}")

    print(f"Deployed/Updated Agent Engine Details: {remote_app}")

    print("\nInteracting with deployed agent engine using a session...")
    session_id_for_remote = None
    session_resource_for_debug = None 
    try:
        session_resource_for_debug = remote_app.create_session(
            user_id="test_user_remote_session"
        )
        print(f"Session resource created: {session_resource_for_debug}")
        
        if isinstance(session_resource_for_debug, dict) and 'id' in session_resource_for_debug:
            session_id_for_remote = session_resource_for_debug['id']
        elif hasattr(session_resource_for_debug, 'name'):
            session_id_for_remote = session_resource_for_debug.name
        elif isinstance(session_resource_for_debug, str):
            session_id_for_remote = session_resource_for_debug
        else:
            print(f"Could not determine session ID from session_resource: {session_resource_for_debug}")
            raise ValueError("Session ID not found in expected format.")

        print(f"Using session ID: {session_id_for_remote}")
        print(f"Attempting streaming_agent_run_with_events with session: {session_id_for_remote}")
        
        try: 
            # Try passing arguments for LlmAgent.stream_query via a 'payload' dictionary.
            for event in remote_app.streaming_agent_run_with_events(
                session=session_id_for_remote,
                payload={"message": "Hello, how are you remotely via session?"} 
            ):
                print(f"Remote session event: {event}")
                if isinstance(event, dict) and event.get("type") == "content" and event.get("content"):
                    for part in event["content"].get("parts", []):
                        if "text" in part:
                            print(f"Remote agent response text (from event): {part['text']}")
            print("Finished streaming_agent_run_with_events.")
        except TypeError as te: 
            print(f"TypeError during streaming_agent_run_with_events: {te}")
            print("This likely indicates an incorrect keyword argument for the user utterance.")
        except Exception as e_stream: 
            print(f"Error during streaming_agent_run_with_events: {e_stream}")
            if hasattr(e_stream, 'response') and hasattr(e_stream.response, 'text'): 
                print(f"Error details (response text): {e_stream.response.text}")
            elif hasattr(e_stream, 'details'): 
                 print(f"Error details (gRPC): {e_stream.details()}")

    except AttributeError as ae_session: 
        print(f"AttributeError during session setup or on remote_app: {ae_session}")
        print("Attributes available on remote_app object:", dir(remote_app))
        if 'session_resource_for_debug' in locals() and session_resource_for_debug: 
             print("Attributes available on session_resource object:", dir(session_resource_for_debug))
    except Exception as e_outer: 
        print(f"Error during session setup/interaction: {e_outer}")
    finally: 
        print("Remote interaction finished.")

    print("\n--- Listing All Agent Engines ---")
    all_agent_engines = list(agent_engines.list())
    if all_agent_engines:
        for agent_engine_item in all_agent_engines:
            print(f"Found Agent: {agent_engine_item.display_name}: {agent_engine_item.resource_name}")
    else:
        print("No agent engines found in the project.")
    print("--- End Listing ---")

if __name__ == "__main__":
    asyncio.run(main())
