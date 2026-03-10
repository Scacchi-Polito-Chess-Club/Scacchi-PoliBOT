# Scacchi PoliBOT

Telegram bot to create Lichess tournaments with notifications.

## Features

- Create Lichess tournaments (Bullet, Blitz, Chess960)
- Telegram notifications with tournament links
- Runs on your own server

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo>
cd Scacchi-PoliBOT
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your tokens:

```bash
cp .env.example .env
# Edit .env with your Telegram and Lichess tokens
```

### 3. Install systemd service

```bash
sudo bash setup.sh
```

This will:
- Create logs directory
- Generate systemd service file
- Enable auto-start on reboot

**Note:** If logs directory has wrong permissions (run as root issue):

```bash
sudo chown -R $USER:$USER logs
```

### 4. Start the bot

```bash
sudo systemctl start scacchi-bot
```

## Commands

| Command      | Type       |
|--------------|-----------|
| `/start`     | Show menu |
| `/bullet`    | 1+0 Bullet |
| `/blitz`     | 2+1 Blitz  |
| `/chess960`  | 3+2 Chess960 |
| `/help`      | Help     |

## Usage

```bash
# Start/Stop/Restart
sudo systemctl start scacchi-bot
sudo systemctl stop scacchi-bot
sudo systemctl restart scacchi-bot

# Enable/Disable auto-start on boot
sudo systemctl enable scacchi-bot
sudo systemctl disable scacchi-bot

# Check status
sudo systemctl status scacchi-bot

# View logs
tail -f logs/bot.log
```

## Project Structure

```
Scacchi-PoliBOT/
├── src/
│   ├── bot.py          # Main entry point
│   ├── config/         # Configuration (tokens, constants)
│   ├── services/       # Lichess and Telegram APIs
│   ├── handlers/       # Message handling logic
│   ├── models/         # Pydantic models
│   └── utils/          # Logging and utilities
├── setup.sh            # Systemd service installer
└── .env                # Environment variables
```

## Requirements

- Python 3.8+
- `requests` library
- `python-dotenv`
- Pydantic

## Environment Variables

Create a `.env` file from `.env.example` and fill in:

| Variable | Description |
|----------|-------------|
| `TELEGRAM_TOKEN` | Get from @BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID |
| `TELEGRAM_TOPIC_ID` | Your topic/forum ID (optional) |
| `LICHESS_TOKEN` | API token from Lichess settings |
| `TEAM_ID` | Your Lichess team ID |
