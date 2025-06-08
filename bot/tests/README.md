# Bot Tests

This directory contains tests for the Slack bot components.

## Test Structure

- `test_simple.py` - Unit tests for basic functionality and utilities
- `test_fastapi.py` - Tests for FastAPI endpoints (health check, Slack events)
- `test_agent.py` - Tests for the agent module (mention removal functionality)
- `conftest.py` - Shared test fixtures and configuration

## Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run all working tests
uv run pytest tests/test_simple.py tests/test_fastapi.py tests/test_agent.py::TestRemoveMentionString -v

# Run specific test files
uv run pytest tests/test_simple.py -v
uv run pytest tests/test_fastapi.py -v

# Run with coverage (if coverage package is added)
uv run pytest --cov=module tests/
```

## Test Coverage

### Working Tests ✅
- **Mention removal logic** - Tests the regex-based mention removal from Slack messages
- **FastAPI endpoints** - Tests health check and Slack events endpoints structure  
- **Basic utilities** - Tests environment variable mocking and basic functionality

### Tests Requiring Infrastructure 🚧
Some tests require actual Vertex AI and Slack API access and are not suitable for unit testing:
- Agent engine integration tests
- Slack app event handler tests (require valid Slack tokens)
- Full end-to-end message processing tests

## Test Philosophy

The tests focus on:
1. **Pure functions** - Logic that doesn't depend on external services
2. **API structure** - Ensuring endpoints exist and respond correctly
3. **Error handling** - Testing edge cases and validation
4. **Mocking external dependencies** - For isolated unit testing

## Adding New Tests

When adding new tests:
1. Test pure business logic first
2. Mock external dependencies (Vertex AI, Slack API)
3. Use fixtures for reusable test data
4. Keep tests isolated and independent