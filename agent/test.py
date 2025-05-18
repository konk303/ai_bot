import os
from dotenv import load_dotenv
from vertexai import agent_engines

def _get_or_create_session_id(thread_id: str):
    """Get or create a session ID for the given thread ID."""
    # Check if the session ID already exists
    sessions = agent_engine.list_sessions(user_id=thread_id)["sessions"]
    if len(sessions) >= 1:
        return sessions[0]["id"]

    # Create a new session ID
    session = agent_engine.create_session(user_id=thread_id)
    return session["id"]

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

for agent_engine in agent_engines.list():
    print(f"{agent_engine.display_name}: {agent_engine.resource_name}")

agent_engine = agent_engines.get(os.getenv("AGENT_ENGINE_RESOURCE"))

messages = [
    "Hello, how are you?",
    "What is the weather like today?",
    "where is thailand?",
    "what is the geo location of tokyo station?",
    ]

for message in messages:
    for event in agent_engine.stream_query(
            user_id="test_user",
            session_id=_get_or_create_session_id("test_user"),
            message=message,
    ):
        print(event)
