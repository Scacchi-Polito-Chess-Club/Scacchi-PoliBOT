"""Scacchi PoliBOT - Telegram bot to create Lichess tournaments."""

import time
import threading
from datetime import datetime, timedelta
import requests

from src.config import (
    LOG_FILE,
    TELEGRAM_TOKEN,
)
from src.utils import Logger
from src.handlers import MessageHandler

logger = Logger(LOG_FILE)

PUZZLE_SCHEDULE_HOUR = 12
PUZZLE_SCHEDULE_MINUTE = 30
PUZZLE_INTERVAL_DAYS = 2


def seconds_until_next_puzzle(last_sent: datetime | None) -> float:
    """
    Return how many seconds to sleep before sending the next scheduled puzzle.

    Rules:
    - If never sent before, fire at the next 12:30 (today if still in the future,
      otherwise tomorrow).
    - If already sent, fire 2 days after the last send time at 12:30.
    """
    now = datetime.now()

    if last_sent is None:
        # Next 12:30 from now
        candidate = now.replace(
            hour=PUZZLE_SCHEDULE_HOUR,
            minute=PUZZLE_SCHEDULE_MINUTE,
            second=0,
            microsecond=0,
        )
        if candidate <= now:
            candidate += timedelta(days=1)
    else:
        candidate = last_sent.replace(
            hour=PUZZLE_SCHEDULE_HOUR,
            minute=PUZZLE_SCHEDULE_MINUTE,
            second=0,
            microsecond=0,
        ) + timedelta(days=PUZZLE_INTERVAL_DAYS)

    delta = (candidate - now).total_seconds()
    return max(delta, 0)


def puzzle_scheduler(handler: MessageHandler) -> None:
    """Background thread: send a puzzle to the group every 2 days at 12:30."""
    last_sent: datetime | None = None

    while True:
        sleep_for = seconds_until_next_puzzle(last_sent)
        logger.info(
            f"Next scheduled puzzle in {sleep_for / 3600:.1f} hours "
            f"({sleep_for / 86400:.2f} days)"
        )
        time.sleep(sleep_for)

        try:
            handler.send_scheduled_puzzle()
            last_sent = datetime.now()
            logger.info("Scheduled puzzle sent successfully.")
        except Exception as e:
            logger.error(f"Scheduled puzzle error: {str(e)[:100]}")
            # Retry after 5 minutes instead of skipping the whole cycle
            time.sleep(300)


def main():
    """Start the bot."""
    logger.info("Starting Scacchi PoliBOT")
    handler = MessageHandler()

    # Start the puzzle scheduler in a daemon thread
    scheduler_thread = threading.Thread(
        target=puzzle_scheduler,
        args=(handler,),
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