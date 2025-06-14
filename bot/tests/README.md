# ボットテスト

このディレクトリにはSlackボットコンポーネントのテストが含まれています。

## テスト構成

- `test_simple.py` - 基本機能とユーティリティのユニットテスト
- `test_fastapi.py` - FastAPIエンドポイントのテスト（ヘルスチェック、Slackイベント）
- `test_agent.py` - エージェントモジュールのテスト（メンション削除機能）
- `conftest.py` - 共有テストフィクスチャと設定

## テスト実行

```bash
# テスト依存関係をインストール
uv sync --extra test

# 動作するテストをすべて実行
uv run pytest tests/test_simple.py tests/test_fastapi.py tests/test_agent.py::TestRemoveMentionString -v

# 特定のテストファイルを実行
uv run pytest tests/test_simple.py -v
uv run pytest tests/test_fastapi.py -v

# カバレッジ付きで実行（coverageパッケージを追加した場合）
uv run pytest --cov=module tests/
```

## テストカバレッジ

### 動作中のテスト ✅
- **メンション削除ロジック** - Slackメッセージからの正規表現ベースのメンション削除テスト
- **FastAPIエンドポイント** - ヘルスチェックとSlackイベントエンドポイント構造のテスト  
- **基本ユーティリティ** - 環境変数モックと基本機能のテスト

### インフラが必要なテスト 🚧
一部のテストは実際のVertex AIとSlack APIアクセスが必要で、ユニットテストには適していません：
- エージェントエンジン統合テスト
- Slackアプリイベントハンドラテスト（有効なSlackトークンが必要）
- エンドツーエンドメッセージ処理テスト

## テスト哲学

テストは以下に焦点を当てています：
1. **純粋関数** - 外部サービスに依存しないロジック
2. **API構造** - エンドポイントが存在し正しく応答することの確認
3. **エラーハンドリング** - エッジケースと検証のテスト
4. **外部依存関係のモック** - 分離されたユニットテストのため

## 新しいテストの追加

新しいテストを追加する際は：
1. まず純粋なビジネスロジックをテスト
2. 外部依存関係（Vertex AI、Slack API）をモック
3. 再利用可能なテストデータにはフィクスチャを使用
4. テストを分離し独立させる