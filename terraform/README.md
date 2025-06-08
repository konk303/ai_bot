# Terraformインフラストラクチャ

このディレクトリにはAI Bot（Slack <-> Gemini）のGoogle Cloudインフラストラクチャ定義が含まれています。

## 概要

Terraformを使用してGoogle Cloudリソースを管理し、以下のコンポーネントをデプロイします：

- **Slackボット**: Cloud Runサービス
- **AIエージェント**: Vertex AI Agent Engine用ストレージ
- **CI/CD**: GitHub Actions用のWorkload Identity
- **シークレット管理**: Secret Manager
- **ストレージ**: Artifact Registry、Cloud Storage

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions   │    │   Cloud Run Bot     │    │ Vertex AI Agent │
│   (CI/CD)          │───▶│   (Slack統合)       │───▶│   (Gemini処理)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Workload Identity  │    │ Secret Manager  │    │ Cloud Storage   │
│ Pool              │    │ (認証情報)       │    │ (ステージング)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ディレクトリ構成

```
terraform/
├── main.tf              # メイン構成とモジュール呼び出し
├── variables.tf         # 変数定義
├── terraform.tfvars     # 変数値（プロジェクトID等）
└── modules/
    ├── backend/         # Terraformステート管理用ストレージ
    ├── bot/            # ボット関連リソース
    └── agent/          # エージェント関連リソース
```

## 主要リソース

### 1. ボットモジュール (`modules/bot/`)

#### Cloud Runサービス
- **サービス名**: `ai-bot`
- **リージョン**: `asia-northeast1`
- **スケーリング**: 0-40インスタンス
- **ヘルスチェック**: `/healthz`エンドポイント

#### Secret Manager
- `slack-token`: Slack Bot Token
- `slack-secret`: Slack Signing Secret  
- `agent-engine`: Vertex AI Agent Engine リソース名

#### GitHub Actions統合
- **Workload Identity Pool**: `gh-actions`
- **サービスアカウント**: `bot-deployer`
- **権限**: Artifact Registry書き込み、Cloud Run デプロイ

#### Artifact Registry
- **リポジトリ**: `ai-bot`
- **形式**: Docker
- **用途**: ボットのコンテナイメージ保存

### 2. エージェントモジュール (`modules/agent/`)

#### Cloud Storage
- **バケット名**: `ai-agent-staging`
- **用途**: Vertex AI Agent Engine用ステージングエリア

### 3. バックエンドモジュール (`modules/backend/`)

#### Terraform State管理
- **バケット名**: `terraform-remote-backend-konk303`
- **バージョニング**: 有効
- **アクセス**: 統一バケットレベルアクセス

## 使用方法

### 1. 初期セットアップ

```bash
# Terraformディレクトリに移動
cd terraform

# Google Cloud認証
gcloud auth application-default login

# Terraform初期化
terraform init
```

### 2. 設定確認

```bash
# 実行計画の確認
terraform plan

# 変数の確認
terraform console
> var.project
> var.region
```

### 3. デプロイ

```bash
# インフラストラクチャのデプロイ
terraform apply

# 特定のモジュールのみデプロイ
terraform apply -target=module.bot
```

### 4. 出力値の確認

```bash
# 重要な出力値を表示
terraform output

# 特定の出力値
terraform output bot-uri
terraform output gh-actions-service-account-name
```

## 必要な権限

Terraformを実行するユーザー/サービスアカウントには以下の権限が必要です：

```yaml
- roles/editor                    # プロジェクト編集者
- roles/iam.securityAdmin        # IAM管理
- roles/serviceusage.serviceUsageAdmin  # API有効化
```

## 環境変数

以下の環境変数を設定してください：

```bash
export GOOGLE_PROJECT="your-project-id"
export GOOGLE_REGION="asia-northeast1"
```

## シークレットの設定

デプロイ後、以下のシークレットを手動で設定する必要があります：

```bash
# Slack Bot Token
gcloud secrets versions add slack-token --data="xoxb-your-slack-bot-token"

# Slack Signing Secret
gcloud secrets versions add slack-secret --data="your-slack-signing-secret"

# Agent Engine Resource
gcloud secrets versions add agent-engine --data="projects/your-project/locations/asia-northeast1/agentEngines/your-agent"
```

## 有効化されるGoogle Cloud API

```yaml
- aiplatform.googleapis.com          # Vertex AI
- run.googleapis.com                 # Cloud Run
- secretmanager.googleapis.com       # Secret Manager
- artifactregistry.googleapis.com    # Artifact Registry
- storage.googleapis.com             # Cloud Storage
- iam.googleapis.com                 # IAM
- maps-backend.googleapis.com        # Google Maps API
- drive.googleapis.com               # Google Drive API
```

## トラブルシューティング

### よくある問題

1. **APIが有効化されていない**
   ```bash
   gcloud services enable run.googleapis.com
   ```

2. **権限不足**
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="user:your-email@domain.com" \
     --role="roles/editor"
   ```

3. **Terraformステートのロック**
   ```bash
   terraform force-unlock LOCK_ID
   ```

### ログの確認

```bash
# Cloud Runサービスのログ
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Terraform操作ログ
terraform show
```

## セキュリティ考慮事項

- ✅ Secret Managerでの認証情報管理
- ✅ Workload Identityによるキーレス認証
- ✅ Cloud Storageのpublic access prevention
- ✅ 最小権限の原則に基づくIAM設定
- ✅ GitHub Actions用の条件付きアクセス

## 監視・ログ

- **Cloud Monitoring**: サービスの監視
- **Cloud Logging**: アプリケーションログ
- **Cloud Trace**: リクエストトレース

## コスト最適化

- **Cloud Run**: 0インスタンスからのスケーリング
- **Secret Manager**: 最小限のシークレット使用
- **Storage**: 適切なライフサイクル管理

## 更新・メンテナンス

### 定期的なタスク

1. **Terraformプロバイダの更新**
2. **セキュリティパッチの適用**
3. **リソースの使用状況確認**
4. **コスト分析とレビュー**

### 破棄

⚠️ **注意**: 以下のコマンドは全てのリソースを削除します

```bash
terraform destroy
```