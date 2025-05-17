"""
FastAPI Slack Bot.

Handles requests from Slack using FastAPI and SocketModeHandler.
"""
import os
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request
from module.app import app

app_handler = SlackRequestHandler(app)
api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@api.post("/slack/events")
async def endpoint(req: Request):
    """Handle incoming Slack events."""
    return await app_handler.handle(req)


@api.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}


# socket mode on direct run
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        pass  # Ctrl+C が押された時はエラーではなく正常終了とする.
