"""Scacchi PoliBOT - Telegram bot to create Lichess tournaments."""

import requests

from src.config import (
    LOG_FILE,
    TELEGRAM_TOKEN,
)
from src.utils import Logger
from src.handlers import MessageHandler

logger = Logger(LOG_FILE)


def main():
    """Start the bot."""

    # Initialize message handler
    logger.info("Starting Scacchi PoliBOT")
    handler = MessageHandler()

    # Start polling
    offset = 0

    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            )
            data = response.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    handler.handle_message(update)
                elif "callback_query" in update:
                    handler.handle_callback(update)

        except Exception as e:
            logger.error(f"Polling error: {str(e)[:100]}")


if __name__ == "__main__":
    main()
