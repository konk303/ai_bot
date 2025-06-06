from google.adk.agents import Agent
from google.adk.tools import google_search

MODEL = "gemini-2.0-flash"


root_agent = Agent(
    name="google_web_search_agent",
    model=MODEL,
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    # google_search is a pre-built tool which allows the agent to perform Google searches.
    tools=[google_search]
)
