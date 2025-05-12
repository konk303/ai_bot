"""
This file implements a Slack bot using the slack_bolt library.

It handles incoming messages (DMs and mentions), processes them using an AI agent,
allows for message deletion via reactions, and defines a slash command.
"""
import os
from slack_bolt import App
from . import agent

SLACK_BOT_USER_ID = "U08QRHY4R42"  # BotのユーザID
SLACK_DELETE_REACTION = "del_gemini"  # 削除用のリアクションを作成しておく

# ボットトークンを渡してアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# https://tools.slack.dev/bolt-python/ja-jp/getting-started/
# https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.event("message")
def event_message(event, say):
    """Slack Apps に対する DM で発言された時に返信する."""
    # ボットとの DM 以外を除外する.
    if event.get("channel_type") != "im":
        return

    thread_id = event["thread_ts"] if "thread_ts" in event else event["ts"]
    say(
        {
            "text": agent.create_answer(str(thread_id), event["text"]),
            "thread_ts": event["ts"],
        }
    )


@app.event("app_mention")
def event_mention(event, say):
    """ボットがメンションされた場合に返信する."""
    thread_id = event["thread_ts"] if "thread_ts" in event else event["ts"]
    say(
        {
            "text": agent.create_answer(str(thread_id), event["text"]),
            "thread_ts": event["ts"],
        }
    )


@app.event("reaction_added")
def message_delete(event):
    """削除用のリアクションがついた場合に発言を削除する."""
    if (
        event["reaction"] == SLACK_DELETE_REACTION
        and event["item_user"] == SLACK_BOT_USER_ID
    ):
        app.client.chat_delete(
            channel=event["item"]["channel"], ts=event["item"]["ts"]
        )


@app.command("/gemini")
def handle_slash_command(ack, client, command):
    """スラッシュコマンドを実行する."""
    ack()

    def post_ephemeral_message(text):
        client.chat_postEphemeral(
            channel=command["channel_id"], user=command["user_id"], text=text
        )

    # /gemini [text] の [text] 部分.
    split = command["text"].split(" ")
    subcommand, _ = split[0], split[1:]

    # bot の使い方を表示する.
    if subcommand == "help":
        post_ephemeral_message(
            "\n".join(
                [
                    "1. Gemini をメンションすると Azure OpenAI Service (ChatGPT) からのレスポンスが返されます。",
                    "2. スレッド内でやり取りを繰り返すと、それまでの会話を考慮した回答がおこなわれます。",
                    "3. スレッド内でもメンションは必要です。",
                    "4. MonoChat との DM でも利用可能です。この場合はメンション不要です。",
                    "5. MonoChat からの返信に :del_monochat: でリアクションすると返信を削除できます。",
                ]
            )
        )
        return

    post_ephemeral_message("Not Implemented")
