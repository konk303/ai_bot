"""
This file defines an agent that interacts with a Vertex AI agent engine.

It handles creating answers to user messages, managing user sessions,
and preprocessing input text by removing mentions.
"""
import os
import re
from markdown_to_mrkdwn import SlackMarkdownConverter
from vertexai import agent_engines

agent_engine = agent_engines.get(os.getenv("AGENT_ENGINE_RESOURCE"))


def create_answer(thread_id: str, message: str):
    """Create an answer for the given user and session."""
    md_converter = SlackMarkdownConverter()
    answers = []
    try:
        for event in agent_engine.stream_query(
            user_id=thread_id,
            session_id=_get_or_create_session_id(thread_id),
            message=_remove_mention_string(message),
        ):
            print(event)
            result = event["content"]["parts"][0]
            if "text" in result:
                answers.append(result["text"])
    except Exception as e:
        answers.extend(
            [
                "メッセージを処理できませんでした。もう一度実行してみてください。:bow:",
                "※本メッセージはGeminiからの返答ではありません。",
                "",
                "",
                "エラー詳細",
                "```",
                str(e),
                "```",
            ]
        )
    return md_converter.convert("\n".join(answers))


def _get_or_create_session_id(thread_id: str):
    """Get or create a session ID for the given thread ID."""
    # Check if the session ID already exists
    sessions = agent_engine.list_sessions(user_id=thread_id)["sessions"]
    if len(sessions) >= 1:
        return sessions[0]["id"]

    # Create a new session ID
    session = agent_engine.create_session(user_id=thread_id)
    return session["id"]


def _remove_mention_string(text: str) -> str:
    """テキストからメンション文字列を削除する."""
    return re.sub(r"<@.+?>", "", text, 1).strip()
