# Railway CLI でのデータエクスポート方法

## 📋 事前準備

### 1. Railway CLI インストール
```bash
# Node.js が必要（未インストールの場合は先にインストール）
npm install -g @railway/cli
```

### 2. Railway CLI にログイン
```bash
railway login
```
ブラウザが開くので、GitHubアカウントでログインする

## 💾 データダウンロード手順

### 1. プロジェクトに接続
```bash
# プロジェクトディレクトリに移動
cd /path/to/discord-memo

# Railwayプロジェクトにリンク
railway link
```
プロジェクト一覧が表示されるので、`discord-memo` を選択

### 2. データファイルをダウンロード
```bash
# user_data.json をローカルにダウンロード
railway run cat user_data.json > user_data_backup.json
```

### 3. データの確認
```bash
# ダウンロードしたファイルの内容確認
cat user_data_backup.json
```

## 🔄 定期バックアップスクリプト

### バックアップスクリプト作成
```bash
#!/bin/bash
# backup-discord-memo.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_FILE="user_data_backup_${DATE}.json"

# バックアップディレクトリ作成
mkdir -p $BACKUP_DIR

# データダウンロード
railway run cat user_data.json > "${BACKUP_DIR}/${BACKUP_FILE}"

echo "✅ バックアップ完了: ${BACKUP_DIR}/${BACKUP_FILE}"
```

### 実行権限付与と実行
```bash
chmod +x backup-discord-memo.sh
./backup-discord-memo.sh
```

## 🚨 トラブルシューティング

### Railway CLI が見つからない場合
```bash
# パスの確認
which railway

# 再インストール
npm uninstall -g @railway/cli
npm install -g @railway/cli
```

### プロジェクトにアクセスできない場合
```bash
# 再ログイン
railway logout
railway login

# プロジェクト一覧確認
railway projects
```

### ファイルが見つからない場合
```bash
# Railway環境でファイル一覧確認
railway run ls -la

# user_data.json の存在確認
railway run ls -la user_data.json
```

## 📝 その他の便利なコマンド

```bash
# Railway環境の環境変数確認
railway run env

# Railway環境でシェル起動
railway shell

# ログ確認
railway logs

# デプロイ状況確認
railway status
```

## ⚠️ 注意事項

- Railway Hobby Plan では、一定期間非アクティブだとサービスが停止する可能性があります
- 重要なデータは定期的にローカルにバックアップすることを強く推奨します
- データダウンロード時は、Discord ボットが稼働中であることを確認してください