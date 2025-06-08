# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This project is a Slack bot powered by Google's Gemini AI, structured as a multi-component system:

- **Bot (`/bot`)**: FastAPI-based Slack bot that handles Slack events and messages
- **Agent (`/agent`)**: AI agent system using Google ADK with hierarchical agent architecture
- **Terraform (`/terraform`)**: Infrastructure as Code for Google Cloud deployment

### Agent Architecture

The system uses a hierarchical agent structure built with Google ADK (Agent Development Kit):

- **Root Agent** (`agent/root_agent/agent.py`): Main orchestrator that delegates to specialized agents
- **Google Search Agent** (`agent/google_search/agent.py`): Handles web search queries
- **Map Agent** (`agent/map/agent.py`): Handles location/direction queries using Google Maps MCP server

### Slack Bot Integration

The bot (`bot/module/app.py`) integrates with Vertex AI Agent Engine and handles:
- Direct messages to the bot
- Mentions in channels
- Message deletion via reactions (`del_gemini`)
- Thread-based conversations with session management

## Development Commands

### Bot Development
```bash
cd bot
uv run main.py  # Run in socket mode for development
uv run uvicorn main:api --reload  # Run FastAPI server
```

### Testing
```bash
cd bot
uv sync --extra test  # Install test dependencies

# Run working tests
uv run pytest tests/test_simple.py tests/test_fastapi.py tests/test_agent.py::TestRemoveMentionString -v

# Run specific test categories
uv run pytest tests/test_simple.py -v  # Basic functionality tests
uv run pytest tests/test_fastapi.py -v  # API endpoint tests
```

### Agent Development
```bash
cd agent
uv run python -c "from root_agent.agent import root_agent; print(root_agent.run('test message'))"
```

### Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Environment Variables

The bot requires these environment variables:
- `SLACK_BOT_TOKEN`: Slack bot token
- `SLACK_SECRET`: Slack signing secret
- `SLACK_APP_TOKEN`: Slack app token (for socket mode)
- `AGENT_ENGINE_RESOURCE`: Vertex AI agent engine resource name
- `GOOGLE_MAPS_API_KEY`: Google Maps API key (for map agent)

## Key Integration Points

- Bot uses Vertex AI Agent Engine (`bot/module/agent.py:12`) to process messages
- Agent system deploys as separate Google Cloud Run service
- Terraform manages infrastructure including workload identity and service accounts
- Session management maintains conversation context per Slack thread