import os
import vertexai
from dotenv import load_dotenv
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from agent import root_agent

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = "gs://ai-agent-staging"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# app = reasoning_engines.AdkApp(
#     agent=root_agent,
#     enable_tracing=True,
# )

# session = app.create_session(user_id="u_123")
# print(session)
# print(app.list_sessions(user_id="u_123"))

# for event in app.stream_query(
#     user_id="u_123",
#     session_id=session.id,
#     message="whats the weather in new york",
# ):
#     print(event)

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ]
)
