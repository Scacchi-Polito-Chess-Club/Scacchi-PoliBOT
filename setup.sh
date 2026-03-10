#!/bin/bash
set -e

# Setup script for Scacchi PoliBOT systemd service
# Usage: sudo bash setup.sh

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run with sudo"
   exit 1
fi

# Verify .env exists (needed for systemd service)
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    exit 1
fi

BOT_PATH=$(pwd)
PYTHON_PATH="${BOT_PATH}/.venv/bin/python"
SERVICE_FILE="/etc/systemd/system/scacchi-bot.service"

# Get the actual user (owner of the directory, not sudo user)
BOT_USER=$(stat -c '%U' "$BOT_PATH")

echo "Setting up Scacchi PoliBOT"
echo "Bot path: $BOT_PATH"
echo "Bot user: $BOT_USER"
echo "Python: $PYTHON_PATH"

# Verify Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Python not found at $PYTHON_PATH"
    echo "Create venv first: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Create logs directory
LOG_DIR="$BOT_PATH/logs"
mkdir -p "$LOG_DIR"
chown "$BOT_USER:$BOT_USER" "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Create systemd service
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Scacchi PoliBOT Telegram
After=network.target

[Service]
Type=simple
User=$BOT_USER
WorkingDirectory=$BOT_PATH
EnvironmentFile=$BOT_PATH/.env
Environment=PYTHONPATH=$BOT_PATH
ExecStart=$PYTHON_PATH $BOT_PATH/src/bot.py
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/bot.log
StandardError=append:$LOG_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

# Reload systemd
systemctl daemon-reload
systemctl enable scacchi-bot

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  sudo systemctl start scacchi-bot    # Start"
echo "  sudo systemctl stop scacchi-bot     # Stop"
echo "  sudo systemctl restart scacchi-bot  # Restart"
echo "  sudo systemctl status scacchi-bot   # Status"
echo "  tail -f logs/bot.log                # View logs"
