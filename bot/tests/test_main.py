"""Tests for main.py FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Mock the agent_engines module before importing main
mock_engine = MagicMock()
mock_agent_engines = MagicMock()
mock_agent_engines.get.return_value = mock_engine

with patch.dict(sys.modules, {'vertexai.agent_engines': mock_agent_engines}):
    with patch.dict(os.environ, {
        'SLACK_BOT_TOKEN': 'xoxb-test-token',
        'SLACK_SECRET': 'test-secret',
        'AGENT_ENGINE_RESOURCE': 'test-resource'
    }):
        with patch('slack_bolt.App'):
            from main import api


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(api)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_healthz_returns_ok(self, client):
        """Test that health check endpoint returns OK status."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestSlackEventsEndpoint:
    """Tests for the Slack events endpoint."""
    
    @patch('main.app_handler.handle')
    def test_slack_events_endpoint_success(self, mock_handle, client):
        """Test successful Slack event handling."""
        mock_handle.return_value = {"success": True}
        
        test_payload = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "text": "Hello bot",
                "user": "U123456"
            }
        }
        
        response = client.post(
            "/slack/events",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        mock_handle.assert_called_once()
    
    @patch('main.app_handler.handle')
    def test_slack_events_endpoint_error_handling(self, mock_handle, client):
        """Test error handling in Slack events endpoint."""
        mock_handle.side_effect = Exception("Handler error")
        
        test_payload = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "text": "Hello bot",
                "user": "U123456"
            }
        }
        
        with pytest.raises(Exception):
            client.post(
                "/slack/events",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )