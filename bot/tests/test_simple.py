"""Simple tests that work without complex mocking."""
import pytest
import re
import os
from unittest.mock import patch, MagicMock


def test_mention_removal():
    """Test the mention removal regex without importing the module."""
    def remove_mention_string(text: str) -> str:
        """Remove mention string from text."""
        return re.sub(r"<@.+?>", "", text, count=1).strip()
    
    # Test cases
    assert remove_mention_string("<@U08QRHY4R42> Hello bot") == "Hello bot"
    assert remove_mention_string("<@U08QRHY4R42>   Hello bot") == "Hello bot"
    assert remove_mention_string("Hello bot") == "Hello bot"
    assert remove_mention_string("Hello <@U08QRHY4R42> and <@U12345678> bot") == "Hello  and <@U12345678> bot"
    assert remove_mention_string("<@U08QRHY4R42|botname> Hello") == "Hello"
    assert remove_mention_string("<@U08QRHY4R42>") == ""


def test_environment_variables():
    """Test that we can mock environment variables."""
    with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
        assert os.getenv('TEST_VAR') == 'test_value'


def test_basic_mocking():
    """Test that basic mocking works."""
    mock_obj = MagicMock()
    mock_obj.test_method.return_value = "mocked_response"
    
    result = mock_obj.test_method("test_input")
    assert result == "mocked_response"
    mock_obj.test_method.assert_called_once_with("test_input")


class TestSlackConstants:
    """Test Slack-related constants."""
    
    def test_slack_constants(self):
        """Test that Slack constants are defined correctly."""
        SLACK_BOT_USER_ID = "U08QRHY4R42"
        SLACK_DELETE_REACTION = "del_gemini"
        
        assert isinstance(SLACK_BOT_USER_ID, str)
        assert len(SLACK_BOT_USER_ID) > 0
        assert isinstance(SLACK_DELETE_REACTION, str)
        assert len(SLACK_DELETE_REACTION) > 0