# Discord Vault - Discord個人データ保存Bot

[🇺🇸 English Version](README.md)

[![Test](https://github.com/bigdra50/discord-vault/actions/workflows/test.yml/badge.svg)](https://github.com/bigdra50/discord-vault/actions/workflows/test.yml)
[![Security Check](https://github.com/bigdra50/discord-vault/actions/workflows/security.yml/badge.svg)](https://github.com/bigdra50/discord-vault/actions/workflows/security.yml)
[![Deploy](https://github.com/bigdra50/discord-vault/actions/workflows/deploy.yml/badge.svg)](https://github.com/bigdra50/discord-vault/actions/workflows/deploy.yml)

個人用のデータを安全に保存・管理できるDiscord Botです。各ユーザーが自分専用のデータストレージを持ち、パスワードやメモなどの情報を保存できます。

## 必要環境

- Python 3.11以上
- Discord.py 2.3.2以上

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd discord-vault
```

### 2. 依存関係のインストール

#### uvを使用する場合（推奨）

```bash
uv sync
```

#### pipを使用する場合

```bash
pip install -r requirements.txt
```

### 3. Discord Botの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリックしてアプリケーションを作成
3. 左メニューの「Bot」を選択
4. 「Reset Token」をクリックしてトークンを取得（一度しか表示されないので注意）

### 4. Botの招待

1. 左メニューの「OAuth2」→「URL Generator」を選択
2. SCOPES で以下を選択：
   - `bot`
   - `applications.commands`
3. BOT PERMISSIONS で以下を選択：
   - Send Messages
   - Use Slash Commands
4. 生成されたURLをブラウザで開いてBotをサーバーに招待

### 5. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、取得したBotトークンを設定：

```
DISCORD_TOKEN=your_bot_token_here
```

### 6. Botの起動

```bash
# uvを使用する場合
uv run python bot.py

# または直接実行
python bot.py
```

起動後、以下のメッセージが表示されれば成功です：

```
vault#8849 としてログインしました
Bot準備完了
```

## 使い方

### コマンド一覧

| コマンド               | 説明               | 使用例                           |
| ---------------------- | ------------------ | -------------------------------- |
| `/save <name> <value>` | データを保存       | `/save password mySecretPass123` |
| `/get [name]`          | データを取得       | `/get password` または `/get`    |
| `/delete <name>`       | データを削除       | `/delete password`               |
| `/list`                | データ名一覧を表示 | `/list`                          |

### 使用例

1. **パスワードを保存**

   ```
   /save gmail_password MyGmailPass123
   ```

   → `✅ **保存完了** データ「gmail_password」を保存しました。`

2. **特定のデータを取得**

   ```
   /get gmail_password
   ```

   → `📄 **データ: gmail_password** \`\`\`MyGmailPass123\`\`\``

3. **すべてのデータを表示**

   ```
   /get
   ```

   → `📋 **保存されたデータ一覧** • **gmail_password**: MyGmailPass123 合計: 1件`

4. **データを削除**

   ```
   /delete gmail_password
   ```

   → `🗑️ **削除完了** データ「gmail_password」を削除しました。`

5. **保存したデータの一覧を確認**
   ```
   /list
   ```
   → `📋 **データ一覧** 保存されたデータはありません。`（データがない場合）

## 制限事項

- **データ名**: 最大50文字、英数字・アンダースコア・ハイフンのみ使用可能
- **データ値**: 最大1,900文字
- **データ数**: 1ユーザーあたり最大100件

## テスト

### 自動テスト実行

```bash
# 単体テスト
uv run python test_bot.py

# 手動テスト（パフォーマンステスト含む）
uv run python manual_test.py
```

### GitHub Actionsでの継続的テスト

このプロジェクトでは以下のワークフローが自動実行されます：

- **テスト** (`test.yml`): プッシュ・プルリクエスト時に自動テスト実行
- **セキュリティチェック** (`security.yml`): 依存関係の脆弱性チェック
- **デプロイ** (`deploy.yml`): mainブランチへのプッシュ時に自動デプロイ準備

## Railway へのデプロイ

### 自動デプロイ（GitHub Actions）

1. Railwayアカウントを作成
2. GitHubリポジトリをRailwayに接続
3. 環境変数を設定：
   - `DISCORD_TOKEN`: Botのトークン
4. mainブランチにプッシュすると自動デプロイ

### 手動デプロイ

1. **requirements.txt の生成**

   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   ```

2. **Railway でのデプロイ**
   - [Railway](https://railway.app/)にサインイン
   - 「New Project」→「Deploy from GitHub repo」を選択
   - リポジトリを選択
   - 環境変数 `DISCORD_TOKEN` を設定
   - デプロイ完了を待つ

## 開発

### 開発環境セットアップ

```bash
# 開発依存関係を含めてインストール
uv sync --dev

# テスト実行
uv run python test_bot.py
uv run python manual_test.py

# コード品質チェック
uv run python -m py_compile bot.py
```

## セキュリティ

- すべてのBotの応答は `ephemeral=True` で送信され、送信者にのみ表示されます
- ユーザーIDによってデータは完全に分離されています
- トークンは必ず環境変数で管理し、コードに直接記載しないでください
- 定期的なセキュリティチェックがGitHub Actionsで自動実行されます

## トラブルシューティング

### Botがオンラインにならない

- トークンが正しく設定されているか確認
- `.env`ファイルが正しい場所にあるか確認
- Python環境が正しくセットアップされているか確認
- `uv sync` で依存関係が正しくインストールされているか確認

### スラッシュコマンドが表示されない

- Botの権限設定を確認（Send Messages, Use Slash Commands）
- Botを再起動してコマンドの同期を待つ（最大1時間）
- Discordアプリを再起動
- 手動でコマンドを入力してみる（`/save test hello`）

### 「アプリケーションが応答しませんでした」エラー

- これまでの実装で解決済み（テキスト応答への変更により）
- もし発生した場合は、Botを再起動してください

### データが保存されない

- `user_data.json`ファイルの書き込み権限を確認
- ディスク容量を確認
- テストで確認：`uv run python test_bot.py`

### 「不明な連携」と表示される

- Discord Developer Portalでアプリケーション情報を設定
- Name, Description, Icon を適切に設定
- Discordアプリを再起動

### パフォーマンス問題

- `uv run python manual_test.py` でパフォーマンステスト実行
- 大量データ（100件近く）の場合は応答が遅くなる可能性があります

