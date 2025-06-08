"""Pytest configuration and shared fixtures."""
import pytest
import os
from unittest.mock import patch


@pytest.fixture
def sample_slack_event():
    """Sample Slack event for testing."""
    return {
        "type": "message",
        "text": "Hello bot",
        "user": "U123456",
        "ts": "1234567890.123456",
        "channel": "C123456",
        "channel_type": "im"
    }


@pytest.fixture
def sample_mention_event():
    """Sample Slack mention event for testing."""
    return {
        "type": "app_mention",
        "text": "<@U08QRHY4R42> Hello bot",
        "user": "U123456",
        "ts": "1234567890.123456",
        "channel": "C123456"
    }


@pytest.fixture
def sample_reaction_event():
    """Sample Slack reaction event for testing."""
    return {
        "type": "reaction_added",
        "reaction": "del_gemini",
        "item_user": "U08QRHY4R42",
        "item": {
            "type": "message",
            "channel": "C123456",
            "ts": "1234567890.123456"
        },
        "user": "U654321"
    }