import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from vertexai import agent_engines

agent_engine = agent_engines.get('projects/69263171180/locations/us-central1/reasoningEngines/6920422942245388288')
remote_session = agent_engine.create_session(user_id="u_456")

# ボットトークンを渡してアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'こんにちは' を含むメッセージをリッスンします
# 指定可能なリスナーのメソッド引数の一覧は以下のモジュールドキュメントを参考にしてください：
# https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.event("message")
def event_message(event, say):
    """
    Slack Apps に対する DM で発言された時に返信する.
    """
    # ボットとの DM 以外を除外する.
    if event.get("channel_type") != "im":
        return

    for event in agent_engine.stream_query(
        user_id="u_456",
        session_id=remote_session["id"],
        message=event["text"]
    ):
        result = event['content']['parts'][0]
        if 'text' in result:
            say(result['text'])


@app.action("button_click")
def action_button_click(body, ack, say):
    # アクションを確認したことを即時で応答します
    ack()
    # チャンネルにメッセージを投稿します
    say(f"<@{body['user']['id']}> さんがボタンをクリックしました！")
    for event in agent_engine.stream_query(
        user_id="u_456",
        session_id=remote_session["id"],
        message="whats the weather in new york",
    ):
        result = event['content']['parts'][0]
        if 'text' in result:
            say(result['text'])

if __name__ == "__main__":
    # アプリを起動して、ソケットモードで Slack に接続します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
