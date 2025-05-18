import asyncio
import os
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from root_agent.create_agent import create_agent

DISPLAY_NAME = "gemini_agent"

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = "gs://ai-agent-staging"

async def main():
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    # # Local testing
    # local_test_agent, local_test_exit_stack = await create_agent()
    # async with local_test_exit_stack:
    #     app = reasoning_engines.AdkApp(
    #         agent=local_test_agent,
    #         enable_tracing=True,
    #     )
    #     for event in app.stream_query(
    #             user_id="u_123",
    #             message="whats the weather in new york",
    #     ):
    #         print(event)

    remote_apps = list(agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"'))

    if len(remote_apps) > 1:
        for remote_app in remote_apps[1:]:
            print("delete old agent engine")
            remote_app.delete(force=True)

    agent, _ = await create_agent()

    if len(remote_apps) == 0:
        print("create new agent engine")
        remote_app = agent_engines.create(
            display_name=DISPLAY_NAME,
            agent_engine=agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]"
            ],
            extra_packages=[
                "root_agent",
                "map",
                "gdrive",
                "google_search",
            ]
        )
    else:
        print("update existing agent engine")
        remote_app = remote_apps[0].update(
            display_name=DISPLAY_NAME,
            agent_engine=agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]"
            ],
            extra_packages=[
                "root_agent",
                "map",
                "gdrive",
                "google_search",
            ]
        )

# print(remote_app)
# for event in remote_app.stream_query(
#         user_id="test_user",
#         message="Hello, how are you?",
# ):
#     print(event)

# for agent_engine in agent_engines.list():
#     print(f"{agent_engine.display_name}: {agent_engine.resource_name}")
#     # agent_engine.delete(force=True)

if __name__ == "__main__":
    asyncio.run(main())
