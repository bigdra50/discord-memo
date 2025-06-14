# Discord Memo - Personal Note Storage Discord Bot

[🇯🇵 日本語版はこちら / Japanese Version](README.jp.md)

[![Test](https://github.com/bigdra50/discord-memo/actions/workflows/test.yml/badge.svg)](https://github.com/bigdra50/discord-memo/actions/workflows/test.yml)
[![Security Check](https://github.com/bigdra50/discord-memo/actions/workflows/security.yml/badge.svg)](https://github.com/bigdra50/discord-memo/actions/workflows/security.yml)
[![Deploy](https://github.com/bigdra50/discord-memo/actions/workflows/deploy.yml/badge.svg)](https://github.com/bigdra50/discord-memo/actions/workflows/deploy.yml)

A Discord bot for storing and managing personal notes and lightweight data. Each user has their own dedicated data storage for notes, settings, and other non-sensitive information.

## Requirements

- Python 3.11 or higher
- Discord.py 2.3.2 or higher

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd discord-vault
```

### 2. Install Dependencies

#### Using uv (Recommended)

```bash
uv sync
```

#### Using pip

```bash
pip install -r requirements.txt
```

### 3. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" to create an application
3. Select "Bot" from the left menu
4. Click "Reset Token" to get your token (note: only shown once)

### 4. Invite Bot

1. Select "OAuth2" → "URL Generator" from the left menu
2. Select the following SCOPES:
   - `bot`
   - `applications.commands`
3. Select the following BOT PERMISSIONS:
   - Send Messages
   - Use Slash Commands
4. Open the generated URL in browser to invite bot to your server

### 5. Environment Variable Setup

```bash
cp .env.example .env
```

Edit the `.env` file and set your bot token:

```
DISCORD_TOKEN=your_bot_token_here
```

### 6. Start the Bot

```bash
# Using uv
uv run python bot.py

# Or direct execution
python bot.py
```

If successful, you should see this message:

```
vault#8849 としてログインしました
Bot準備完了
```

## Usage

### Command List

| Command                | Description           | Example                          |
| ---------------------- | --------------------- | -------------------------------- |
| `/save <name> <value>` | Save data             | `/save password mySecretPass123` |
| `/get [name]`          | Retrieve data         | `/get password` or `/get`        |
| `/delete <name>`       | Delete data           | `/delete password`               |
| `/list`                | Show data name list   | `/list`                          |

### Usage Examples

1. **Save Password**

   ```
   /save gmail_password MyGmailPass123
   ```

   → `✅ **Save Complete** Data "gmail_password" has been saved.`

2. **Retrieve Specific Data**

   ```
   /get gmail_password
   ```

   → `📄 **Data: gmail_password** \`\`\`MyGmailPass123\`\`\``

3. **Show All Data**

   ```
   /get
   ```

   → `📋 **Saved Data List** • **gmail_password**: MyGmailPass123 Total: 1 item`

4. **Delete Data**

   ```
   /delete gmail_password
   ```

   → `🗑️ **Delete Complete** Data "gmail_password" has been deleted.`

5. **Check Saved Data List**
   ```
   /list
   ```
   → `📋 **Data List** No saved data found.` (when no data exists)

## Limitations

- **Data Name**: Maximum 50 characters, alphanumeric characters, underscores, and hyphens only
- **Data Value**: Maximum 1,900 characters
- **Data Count**: Maximum 100 items per user

## Testing

### Automated Test Execution

```bash
# Unit tests
uv run python test_bot.py

# Manual tests (including performance tests)
uv run python manual_test.py
```

### Continuous Testing with GitHub Actions

This project automatically runs the following workflows:

- **Testing** (`test.yml`): Automatic test execution on push/pull request
- **Security Check** (`security.yml`): Dependency vulnerability checks
- **Deploy** (`deploy.yml`): Automatic deployment preparation on push to main branch

## Deploy to Railway

### Automatic Deployment (GitHub Actions)

1. Create Railway account
2. Connect GitHub repository to Railway
3. Set environment variables:
   - `DISCORD_TOKEN`: Bot token
4. Automatic deployment on push to main branch

### Manual Deployment

1. **Generate requirements.txt**

   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   ```

2. **Deploy on Railway**
   - Sign in to [Railway](https://railway.app/)
   - Select "New Project" → "Deploy from GitHub repo"
   - Select repository
   - Set environment variable `DISCORD_TOKEN`
   - Wait for deployment completion

## Development

### Development Environment Setup

```bash
# Install including development dependencies
uv sync --dev

# Run tests
uv run python test_bot.py
uv run python manual_test.py

# Code quality check
uv run python -m py_compile bot.py
```

## Security

- All bot responses are sent with `ephemeral=True` and only visible to sender
- Data is completely isolated by user ID
- Always manage tokens with environment variables, never hardcode in source
- Regular security checks automatically run via GitHub Actions

## ⚠️ Important Security Notice

### 🚨 Data That Should NOT Be Stored

This bot stores data in **unencrypted plain text**. **DO NOT store** the following sensitive information:

#### 💳 Financial & Payment Information
- Credit card numbers
- Bank account numbers
- PIN codes
- Cryptocurrency wallet private keys

#### 🔐 Authentication Credentials
- Passwords
- API keys & tokens
- OAuth authorization codes
- Two-factor authentication recovery codes

#### 📄 Personal & Legal Documents
- Social Security Numbers
- Passport numbers
- Driver's license numbers
- Health insurance card numbers

#### 🏥 Medical & Health Information
- Medical diagnoses
- Prescription information
- Genetic information

### ✅ Appropriate Use Cases

This bot is ideal for **lightweight memo purposes**:

- Game settings & server information
- Study notes & idea memos
- Project progress
- Public configuration values
- Temporary notes

### 🛡️ For Sensitive Information Management

For secure storage of sensitive information, use dedicated tools:

- [1Password](https://1password.com/)
- [Bitwarden](https://bitwarden.com/)
- [LastPass](https://www.lastpass.com/)
- [KeePass](https://keepass.info/)

### 📊 Data Access Permissions

The stored data can be accessed by:

- **You** (via Discord bot)
- **Railway administrators** (hosting platform)
- **Server administrators** (with physical/virtual server access)

**Important**: This bot is a convenient memo tool, but the security level is not high. Choose appropriate tools based on your use case.

## Troubleshooting

### Bot Won't Come Online

- Check if token is correctly set
- Verify `.env` file is in correct location
- Confirm Python environment is properly set up
- Ensure dependencies are installed with `uv sync`

### Slash Commands Not Appearing

- Check bot permissions (Send Messages, Use Slash Commands)
- Restart bot and wait for command sync (up to 1 hour)
- Restart Discord app
- Try manually typing commands (`/save test hello`)

### "Application Did Not Respond" Error

- This has been resolved in current implementation (by switching to text responses)
- If it still occurs, restart the bot

### Data Not Saving

- Check write permissions for `user_data.json` file
- Check disk space
- Verify with test: `uv run python test_bot.py`

### "Unknown Integration" Display

- Set application information in Discord Developer Portal
- Properly configure Name, Description, and Icon
- Restart Discord app

### Performance Issues

- Run performance test: `uv run python manual_test.py`
- Response may be slower with large amounts of data (near 100 items)