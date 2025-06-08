"""Tests for module/app.py Slack event handlers."""
import pytest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Mock the agent_engines module before importing
mock_engine = MagicMock()
mock_agent_engines = MagicMock()
mock_agent_engines.get.return_value = mock_engine

with patch.dict(sys.modules, {'vertexai.agent_engines': mock_agent_engines}):
    # Mock environment variables before importing app
    with patch.dict(os.environ, {
        'SLACK_BOT_TOKEN': 'xoxb-test-token',
        'SLACK_SECRET': 'test-secret',
        'AGENT_ENGINE_RESOURCE': 'test-resource'
    }):
        with patch('slack_bolt.App') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            from module.app import SLACK_BOT_USER_ID, SLACK_DELETE_REACTION
            
            # Import the app after setting up mocks
            app = mock_app


class TestSlackEventHandlers:
    """Tests for Slack event handlers."""
    
    @patch('module.agent.create_answer')
    def test_event_message_dm(self, mock_create_answer):
        """Test DM message handling."""
        mock_create_answer.return_value = "Test response"
        mock_say = MagicMock()
        
        event = {
            "channel_type": "im",
            "text": "Hello bot",
            "ts": "1234567890.123456",
            "user": "U123456"
        }
        
        # Import and call the handler function directly
        from module.app import event_message
        event_message(event, mock_say)
        
        mock_create_answer.assert_called_once_with("1234567890.123456", "Hello bot")
        mock_say.assert_called_once_with({
            "text": "Test response",
            "thread_ts": "1234567890.123456"
        })
    
    @patch('module.agent.create_answer')
    def test_event_message_with_thread(self, mock_create_answer):
        """Test DM message handling with existing thread."""
        mock_create_answer.return_value = "Test response"
        mock_say = MagicMock()
        
        event = {
            "channel_type": "im",
            "text": "Hello bot",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.000000",
            "user": "U123456"
        }
        
        from module.app import event_message
        event_message(event, mock_say)
        
        mock_create_answer.assert_called_once_with("1234567890.000000", "Hello bot")
        mock_say.assert_called_once_with({
            "text": "Test response",
            "thread_ts": "1234567890.123456"
        })
    
    @patch('module.agent.create_answer')
    def test_event_message_non_dm_ignored(self, mock_create_answer):
        """Test that non-DM messages are ignored."""
        mock_say = MagicMock()
        
        event = {
            "channel_type": "channel",
            "text": "Hello bot",
            "ts": "1234567890.123456",
            "user": "U123456"
        }
        
        from module.app import event_message
        event_message(event, mock_say)
        
        mock_create_answer.assert_not_called()
        mock_say.assert_not_called()
    
    @patch('module.agent.create_answer')
    def test_event_mention(self, mock_create_answer):
        """Test mention event handling."""
        mock_create_answer.return_value = "Mention response"
        mock_say = MagicMock()
        
        event = {
            "text": "<@U08QRHY4R42> Hello bot",
            "ts": "1234567890.123456",
            "user": "U123456"
        }
        
        from module.app import event_mention
        event_mention(event, mock_say)
        
        mock_create_answer.assert_called_once_with("1234567890.123456", "<@U08QRHY4R42> Hello bot")
        mock_say.assert_called_once_with({
            "text": "Mention response",
            "thread_ts": "1234567890.123456"
        })
    
    def test_message_delete_correct_reaction(self):
        """Test message deletion with correct reaction and bot user."""
        mock_client = MagicMock()
        
        with patch.object(app, 'client', mock_client):
            event = {
                "reaction": SLACK_DELETE_REACTION,
                "item_user": SLACK_BOT_USER_ID,
                "item": {
                    "channel": "C123456",
                    "ts": "1234567890.123456"
                }
            }
            
            from module.app import message_delete
            message_delete(event)
            
            mock_client.chat_delete.assert_called_once_with(
                channel="C123456",
                ts="1234567890.123456"
            )
    
    def test_message_delete_wrong_reaction(self):
        """Test that wrong reaction doesn't delete message."""
        mock_client = MagicMock()
        
        with patch.object(app, 'client', mock_client):
            event = {
                "reaction": "thumbsup",
                "item_user": SLACK_BOT_USER_ID,
                "item": {
                    "channel": "C123456",
                    "ts": "1234567890.123456"
                }
            }
            
            from module.app import message_delete
            message_delete(event)
            
            mock_client.chat_delete.assert_not_called()
    
    def test_message_delete_wrong_user(self):
        """Test that reaction from non-bot user doesn't delete message."""
        mock_client = MagicMock()
        
        with patch.object(app, 'client', mock_client):
            event = {
                "reaction": SLACK_DELETE_REACTION,
                "item_user": "U999999",
                "item": {
                    "channel": "C123456",
                    "ts": "1234567890.123456"
                }
            }
            
            from module.app import message_delete
            message_delete(event)
            
            mock_client.chat_delete.assert_not_called()


class TestSlashCommand:
    """Tests for slash command handler."""
    
    def test_slash_command_help(self):
        """Test help subcommand."""
        mock_ack = MagicMock()
        mock_client = MagicMock()
        command = {
            "text": "help",
            "channel_id": "C123456",
            "user_id": "U123456"
        }
        
        from module.app import handle_slash_command
        handle_slash_command(mock_ack, mock_client, command)
        
        mock_ack.assert_called_once()
        mock_client.chat_postEphemeral.assert_called_once()
        
        call_args = mock_client.chat_postEphemeral.call_args
        assert call_args[1]["channel"] == "C123456"
        assert call_args[1]["user"] == "U123456"
        assert "gemini をメンション" in call_args[1]["text"]
    
    def test_slash_command_not_implemented(self):
        """Test unimplemented subcommand."""
        mock_ack = MagicMock()
        mock_client = MagicMock()
        command = {
            "text": "unknown",
            "channel_id": "C123456",
            "user_id": "U123456"
        }
        
        from module.app import handle_slash_command
        handle_slash_command(mock_ack, mock_client, command)
        
        mock_ack.assert_called_once()
        mock_client.chat_postEphemeral.assert_called_once()
        
        call_args = mock_client.chat_postEphemeral.call_args
        assert call_args[1]["text"] == "Not Implemented"