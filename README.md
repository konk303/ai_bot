# ai_bot
slack &lt;-> gemini

## 概要
SlackとGoogle Gemini AIを統合したチャットボットシステムです。階層化されたエージェント構造により、様々なクエリに対応します。

## 構成
- **bot/**: Slack統合用のFastAPIベースのボット
- **agent/**: Google ADKを使用したAIエージェントシステム  
- **terraform/**: Google Cloudインフラ管理

## 開発環境セットアップ

### ボット開発
```bash
cd bot
uv sync --extra test  # テスト依存関係を含む
uv run main.py  # ソケットモードで起動
uv run uvicorn main:api --reload  # FastAPIサーバーとして起動
```

### テスト実行
```bash
cd bot
uv sync --extra test
uv run pytest tests/test_simple.py tests/test_fastapi.py tests/test_agent.py::TestRemoveMentionString -v
```

### エージェント開発
```bash
cd agent  
uv sync
uv run python -c "from root_agent.agent import root_agent; print(root_agent.run('テストメッセージ'))"
```

## 機能
- SlackのDMとメンション対応
- スレッド形式での会話継続
- Google検索エージェント統合
- 地図・経路案内エージェント統合
- リアクションによるメッセージ削除機能

## 環境変数
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_SECRET=...
SLACK_APP_TOKEN=xapp-...
AGENT_ENGINE_RESOURCE=projects/.../agentEngines/...
GOOGLE_MAPS_API_KEY=...
```

## 参考リンク
https://cloud.google.com/vertex-ai/generative-ai/pricing?hl=ja#google_models
https://ai.google.dev/gemini-api/docs/pricing
