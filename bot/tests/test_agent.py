"""Tests for module/agent.py integration."""
import pytest
from unittest.mock import patch, MagicMock
import os
import re
import sys

# Mock the agent_engines module before importing
mock_engine = MagicMock()
mock_agent_engines = MagicMock()
mock_agent_engines.get.return_value = mock_engine

with patch.dict(sys.modules, {'vertexai.agent_engines': mock_agent_engines}):
    with patch.dict(os.environ, {'AGENT_ENGINE_RESOURCE': 'test-resource'}):
        from module.agent import create_answer, _get_or_create_session_id, _remove_mention_string


class TestCreateAnswer:
    """Tests for create_answer function."""
    
    @patch('module.agent.agent_engine')
    @patch('module.agent.SlackMarkdownConverter')
    def test_create_answer_success(self, mock_converter_class, mock_agent_engine):
        """Test successful answer creation."""
        # Setup mocks
        mock_converter = MagicMock()
        mock_converter.convert.return_value = "Converted response"
        mock_converter_class.return_value = mock_converter
        
        mock_session_response = {"sessions": [{"id": "session-123"}]}
        mock_agent_engine.list_sessions.return_value = mock_session_response
        
        # Mock streaming events
        mock_events = [
            {
                "content": {
                    "parts": [{"text": "Hello "}]
                }
            },
            {
                "content": {
                    "parts": [{"text": "world!"}]
                }
            }
        ]
        mock_agent_engine.stream_query.return_value = iter(mock_events)
        
        # Test
        result = create_answer("thread-123", "Hello bot")
        
        # Assertions
        mock_agent_engine.list_sessions.assert_called_once_with(user_id="thread-123")
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="thread-123",
            session_id="session-123",
            message="Hello bot"
        )
        mock_converter.convert.assert_called_once_with("Hello world!")
        assert result == "Converted response"
    
    @patch('module.agent.agent_engine')
    @patch('module.agent.SlackMarkdownConverter')
    def test_create_answer_exception_handling(self, mock_converter_class, mock_agent_engine):
        """Test exception handling in create_answer."""
        # Setup mocks
        mock_converter = MagicMock()
        mock_converter.convert.return_value = "Error response"
        mock_converter_class.return_value = mock_converter
        
        mock_agent_engine.list_sessions.side_effect = Exception("API Error")
        
        # Test
        result = create_answer("thread-123", "Hello bot")
        
        # Check that error message is converted and returned
        mock_converter.convert.assert_called_once()
        call_args = mock_converter.convert.call_args[0][0]
        assert "メッセージを処理できませんでした" in call_args
        assert "API Error" in call_args
        assert result == "Error response"
    
    @patch('module.agent.agent_engine')
    @patch('module.agent.SlackMarkdownConverter')
    def test_create_answer_with_non_text_parts(self, mock_converter_class, mock_agent_engine):
        """Test handling of non-text parts in response."""
        # Setup mocks
        mock_converter = MagicMock()
        mock_converter.convert.return_value = "Converted response"
        mock_converter_class.return_value = mock_converter
        
        mock_session_response = {"sessions": [{"id": "session-123"}]}
        mock_agent_engine.list_sessions.return_value = mock_session_response
        
        # Mock events with non-text parts
        mock_events = [
            {
                "content": {
                    "parts": [{"image": "base64data"}]  # Non-text part
                }
            },
            {
                "content": {
                    "parts": [{"text": "Hello!"}]
                }
            }
        ]
        mock_agent_engine.stream_query.return_value = iter(mock_events)
        
        # Test
        result = create_answer("thread-123", "Hello bot")
        
        # Should only include text parts
        mock_converter.convert.assert_called_once_with("Hello!")
        assert result == "Converted response"


class TestGetOrCreateSessionId:
    """Tests for _get_or_create_session_id function."""
    
    @patch('module.agent.agent_engine')
    def test_existing_session(self, mock_agent_engine):
        """Test getting existing session ID."""
        mock_sessions_response = {
            "sessions": [
                {"id": "existing-session-123"},
                {"id": "another-session-456"}
            ]
        }
        mock_agent_engine.list_sessions.return_value = mock_sessions_response
        
        result = _get_or_create_session_id("thread-123")
        
        mock_agent_engine.list_sessions.assert_called_once_with(user_id="thread-123")
        mock_agent_engine.create_session.assert_not_called()
        assert result == "existing-session-123"
    
    @patch('module.agent.agent_engine')
    def test_create_new_session(self, mock_agent_engine):
        """Test creating new session when none exists."""
        mock_sessions_response = {"sessions": []}
        mock_agent_engine.list_sessions.return_value = mock_sessions_response
        mock_agent_engine.create_session.return_value = {"id": "new-session-789"}
        
        result = _get_or_create_session_id("thread-456")
        
        mock_agent_engine.list_sessions.assert_called_once_with(user_id="thread-456")
        mock_agent_engine.create_session.assert_called_once_with(user_id="thread-456")
        assert result == "new-session-789"


class TestRemoveMentionString:
    """Tests for _remove_mention_string function."""
    
    def test_remove_mention_at_start(self):
        """Test removing mention at the start of text."""
        text = "<@U08QRHY4R42> Hello bot"
        result = _remove_mention_string(text)
        assert result == "Hello bot"
    
    def test_remove_mention_with_extra_spaces(self):
        """Test removing mention with extra spaces."""
        text = "<@U08QRHY4R42>   Hello bot"
        result = _remove_mention_string(text)
        assert result == "Hello bot"
    
    def test_no_mention_in_text(self):
        """Test text without mention."""
        text = "Hello bot"
        result = _remove_mention_string(text)
        assert result == "Hello bot"
    
    def test_mention_in_middle_not_removed(self):
        """Test that mention in middle is not removed (only first one)."""
        text = "Hello <@U08QRHY4R42> and <@U12345678> bot"
        result = _remove_mention_string(text)
        assert result == "Hello  and <@U12345678> bot"
    
    def test_complex_mention_format(self):
        """Test complex mention format."""
        text = "<@U08QRHY4R42|botname> Hello"
        result = _remove_mention_string(text)
        assert result == "Hello"
    
    def test_empty_text_after_mention_removal(self):
        """Test text that becomes empty after mention removal."""
        text = "<@U08QRHY4R42>"
        result = _remove_mention_string(text)
        assert result == ""