import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

root_agent = Agent(
    name="gemini_agent",
    model="gemini-2.5-flash-preview-04-17",
    description=(
        "(Japanese)Agent to answer questions about anything."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about anything."
    ),
    tools=[],
)
