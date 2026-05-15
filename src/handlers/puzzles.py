import threading
import time
from typing import List, Optional
from datetime import datetime, timedelta
from src.services import LichessService, TelegramService
from src.utils import Logger
from src.config import (
    LOG_FILE,
    TELEGRAM_PUZZLE_TOPIC_ID,
    TELEGRAM_CHAT_ID,
)

PUZZLE_SCHEDULE_HOUR = 12
PUZZLE_SCHEDULE_MINUTE = 30
PUZZLE_INTERVAL_DAYS = 2

logger = Logger(LOG_FILE)

lichess = LichessService()
telegram = TelegramService()


@staticmethod
def side_to_move(fen: str) -> str:
    """Return 'White' or 'Black' for the player solving the puzzle."""
    try:
        color = fen.split(" ")[1]
        return "Black" if color == "w" else "White"
    except (IndexError, AttributeError):
        return "White"


def build_puzzle_caption(
    rating: int | str,
    themes: str,
    side: str,
    display_difficulty: str,
) -> str:
    """Build the initial puzzle caption (without solution)."""
    return (
        f"🧩 <b>{display_difficulty} Puzzle</b>\n"
        f"🎯 <b>{side} to move</b>\n"
        f"⭐ <b>Rating:</b> {rating}\n"
        f"🏷️ <b>Themes:</b> {themes}\n\n"
        f"💡 Solution in 4 hours\n\n"
    )


def schedule_solution_reveal(
    chat_id: int, topic_id: Optional[int], message_id: int, caption: str, solution: List[str]
) -> None:
    """Schedule editing the caption to reveal the solution after 4 hours."""
    solution_str = ", ".join(solution)
    new_caption = caption.replace(
        "💡 Solution in 4 hours",
        f"💡 <b>Solution:</b> <tg-spoiler>{solution_str}</tg-spoiler>",
    )
    timer = threading.Timer(
        14400,
        telegram.edit_message_caption,
        args=[chat_id, topic_id, message_id, new_caption],
    )
    timer.start()
    logger.info(f"Scheduled solution reveal for message {message_id} in 4 hours.")


def send_puzzle(user_id: int) -> None:
    """Fetch and send a Lichess puzzle to a user in private chat."""
    success, data = lichess.get_puzzle()

    if not success:
        telegram.send_message("❌ Could not fetch puzzle.", chat_id=user_id)
        return

    puzzle = data.get("puzzle", {})
    difficulty = data.get("custom_difficulty", "normal")

    puzzle_id = puzzle.get("id", "?")
    rating = puzzle.get("rating", "?")
    themes = ", ".join(puzzle.get("themes", [])[:3])
    solution = puzzle.get("solution", [])
    fen = puzzle.get("fen", "")
    side = side_to_move(fen)

    color_map = {
        "easier": "green",
        "normal": "brown",
        "harder": "blue",
        "hardest": "purple",
    }
    display_names = {
        "easier": "Easy",
        "normal": "Normal",
        "harder": "Hard",
        "hardest": "Extreme",
    }

    board_theme = color_map.get(difficulty, "brown")
    display_difficulty = display_names.get(difficulty, "Normal")

    photo_url = (
        f"https://lichess1.org/training/export/gif/thumbnail/{puzzle_id}.gif?theme={board_theme}"
    )
    caption = build_puzzle_caption(rating, themes, side, display_difficulty)

    sent_success, message_id = telegram.send_photo(
        photo_url,
        caption=caption,
        chat_id=TELEGRAM_CHAT_ID,
        topic_id=TELEGRAM_PUZZLE_TOPIC_ID,
    )

    if sent_success and message_id:
        schedule_solution_reveal(
            TELEGRAM_CHAT_ID,
            TELEGRAM_PUZZLE_TOPIC_ID,
            message_id,
            caption,
            solution,
        )


def send_scheduled_puzzle() -> None:
    """Fetch and send a Lichess puzzle to the group puzzle topic."""
    if not TELEGRAM_PUZZLE_TOPIC_ID:
        logger.error("TELEGRAM_PUZZLE_TOPIC_ID is not set — cannot send scheduled puzzle.")
        return

    success, data = lichess.get_puzzle()

    if not success:
        logger.error("Scheduled puzzle: could not fetch puzzle from Lichess.")
        return

    puzzle = data.get("puzzle", {})
    difficulty = data.get("custom_difficulty", "normal")

    puzzle_id = puzzle.get("id", "?")
    rating = puzzle.get("rating", "?")
    themes = ", ".join(puzzle.get("themes", [])[:3])
    solution = puzzle.get("solution", [])
    fen = puzzle.get("fen", "")
    side = side_to_move(fen)

    color_map = {
        "easier": "green",
        "normal": "brown",
        "harder": "blue",
        "hardest": "purple",
    }
    display_names = {
        "easier": "Easy",
        "normal": "Normal",
        "harder": "Hard",
        "hardest": "Extreme",
    }

    board_theme = color_map.get(difficulty, "brown")
    display_difficulty = display_names.get(difficulty, "Normal")

    photo_url = (
        f"https://lichess1.org/training/export/gif/thumbnail/{puzzle_id}.gif?theme={board_theme}"
    )
    caption = build_puzzle_caption(rating, themes, side, display_difficulty)

    sent_success, message_id = telegram.send_photo(
        photo_url,
        caption=caption,
        chat_id=TELEGRAM_CHAT_ID,
        topic_id=TELEGRAM_PUZZLE_TOPIC_ID,
    )

    if sent_success and message_id:
        schedule_solution_reveal(
            TELEGRAM_CHAT_ID,
            TELEGRAM_PUZZLE_TOPIC_ID,
            message_id,
            caption,
            solution,
        )
        logger.info(
            f"Scheduled puzzle {puzzle_id} sent to group topic {TELEGRAM_PUZZLE_TOPIC_ID}."
        )
    else:
        logger.error("Scheduled puzzle: failed to send photo to group topic.")


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


def puzzle_scheduler() -> None:
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
            send_scheduled_puzzle()
            last_sent = datetime.now()
            logger.info("Scheduled puzzle sent successfully.")
        except Exception as e:
            logger.error(f"Scheduled puzzle error: {str(e)[:100]}")
            # Retry after 5 minutes instead of skipping the whole cycle
            time.sleep(300)
