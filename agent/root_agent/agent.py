"""Client agent for the Gemini model, combining whole agents."""
from .create_agent import create_agent

root_agent = create_agent()
