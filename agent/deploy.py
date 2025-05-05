import os
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from agents import root_agent

DISPLAY_NAME = "gemini_agent"

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = "gs://ai-agent-staging"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

remote_apps = list(agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"'))

if len(remote_apps) > 1:
    for remote_app in remote_apps[1:]:
        print("delete old agent engine")
        remote_app.delete(force=True)

if len(remote_apps) == 0:
    print("create new agent engine")
    remote_app = agent_engines.create(
        display_name=DISPLAY_NAME,
        agent_engine=root_agent,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"
        ],
        extra_packages=[
            "agents"
        ]
    )
else:
    print("update existing agent engine")
    remote_app = remote_apps[0].update(
        display_name=DISPLAY_NAME,
        agent_engine=root_agent,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"
        ],
        extra_packages=[
            "agents"
        ]
    )

print(remote_app)
for event in remote_app.stream_query(
        user_id="test_user",
        message="Hello, how are you?",
):
    print(event)

for agent_engine in agent_engines.list():
    print(f"{agent_engine.display_name}: {agent_engine.resource_name}")
    # agent_engine.delete(force=True)
