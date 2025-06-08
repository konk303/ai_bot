# Slack Bot

SlackとGoogle Gemini AIを統合したボットアプリケーションです。

## 機能
- **DM対応**: ボットとの直接メッセージでのやり取り
- **メンション対応**: チャンネルでボットをメンションして利用
- **スレッド継続**: スレッド内での会話履歴を保持
- **削除機能**: `:del_gemini:` リアクションでボットの返信を削除
- **スラッシュコマンド**: `/gemini help` でヘルプ表示

## 開発

### 環境セットアップ
```bash
uv sync --extra test  # 依存関係とテスト用パッケージをインストール
```

### 実行方法
```bash
# ソケットモードで起動（開発用）
uv run main.py

# FastAPIサーバーとして起動（本番用）
uv run uvicorn main:api --reload
```

### テスト実行
```bash
# 全テスト実行
uv run pytest tests/test_simple.py tests/test_fastapi.py tests/test_agent.py::TestRemoveMentionString -v

# カテゴリ別テスト
uv run pytest tests/test_simple.py -v      # 基本機能テスト
uv run pytest tests/test_fastapi.py -v     # APIエンドポイントテスト
```

## 必要な環境変数
```
SLACK_BOT_TOKEN=xoxb-...         # Slack Bot Token
SLACK_SECRET=...                 # Slack Signing Secret  
SLACK_APP_TOKEN=xapp-...         # Slack App Token（ソケットモード用）
AGENT_ENGINE_RESOURCE=...        # Vertex AI Agent Engine リソース名
```

## アーキテクチャ
- **main.py**: FastAPIアプリケーションとエンドポイント定義
- **module/app.py**: Slack Boltアプリとイベントハンドラ
- **module/agent.py**: Vertex AI Agent Engineとの統合

## 参考リンク
https://tools.slack.dev/bolt-python/ja-jp/getting-started/
