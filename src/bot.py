"""Scacchi PoliBOT - Telegram bot to create Lichess tournaments."""

import threading
import requests

from src.config import (
    LOG_FILE,
    TELEGRAM_TOKEN,
)
from src.utils import Logger
from src.handlers import MessageHandler, puzzle_scheduler

logger = Logger(LOG_FILE)


def main():
    """Start the bot."""
    logger.info("Starting Scacchi PoliBOT")
    handler = MessageHandler()

    # Start the puzzle scheduler in a daemon thread
    scheduler_thread = threading.Thread(
        target=puzzle_scheduler,
        args=(),
        daemon=True,
        name="PuzzleScheduler",
    )
    scheduler_thread.start()
    logger.info("Puzzle scheduler started.")

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
