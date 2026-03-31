"""Handle Telegram messages and callbacks."""

from typing import Dict, List, Any
from src.config import AUTHORIZED_USERS, TOURNAMENT_TYPES, COMMANDS, LOG_FILE, TELEGRAM_CHAT_ID, TELEGRAM_PUZZLE_TOPIC_ID
from src.services import LichessService, TelegramService
from src.utils import Logger
import threading

logger = Logger(LOG_FILE)


class MessageHandler:
    """Process incoming Telegram messages."""

    def __init__(self):
        self.lichess = LichessService()
        self.telegram = TelegramService()

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        return user_id in AUTHORIZED_USERS

    def get_keyboard(self) -> List[List[Dict[str, str]]]:
        """Return inline keyboard."""
        return [
            [{"text": "1+0 Bullet", "callback_data": "tournament_bullet10"}],
            [{"text": "2+1 Blitz", "callback_data": "tournament_blitz20"}],
            [{"text": "3+2 Chess960", "callback_data": "tournament_chess960"}],
        ]

    def handle_message(self, update: Dict[Any, Any]) -> None:
        """Handle text message."""
        message = update.get("message", {})
        user_id = message.get("from", {}).get("id")
        username = message.get("from", {}).get("username", "Unknown")
        text = message.get("text", "")

        if not self.is_authorized(user_id):
            self.telegram.send_message("❌ Not authorized", chat_id=user_id)
            logger.warning(f"Unauthorized access from {username} ({user_id})")
            return

        if text == "/start":
            self.telegram.send_keyboard(
                "🏆 <b>Lichess Tournament Manager</b>\n\nSelect tournament type:",
                self.get_keyboard(),
                chat_id=user_id,
            )

        elif text == "/help":
            self.telegram.send_message(
                "/start - Menu\n/bullet - 1+0 Bullet\n/blitz - 2+1 Blitz\n/chess960 - 3+2 Chess960\n/puzzle - Puzzle",
                chat_id=user_id,
            )
        elif text == "/puzzle":
            self._send_puzzle(user_id)

        elif text in COMMANDS:
            tournament_id = COMMANDS[text]
            self._create_tournament(tournament_id, username, user_id)

    def handle_callback(self, update: Dict[Any, Any]) -> None:
        """Handle callback button press."""
        callback = update.get("callback_query", {})
        user_id = callback.get("from", {}).get("id")
        username = callback.get("from", {}).get("username", "Unknown")
        data = callback.get("data", "")

        if not self.is_authorized(user_id):
            self.telegram.send_message("❌ Not authorized", chat_id=user_id)
            logger.warning(f"Unauthorized callback from {username} ({user_id})")
            return

        if data.startswith("tournament_"):
            tournament_id = data.split("_")[1]
            self._create_tournament(tournament_id, username, user_id)

    def _create_tournament(self, tournament_id: str, username: str, user_id: int) -> None:
        """Create tournament and notify."""
        tournament = TOURNAMENT_TYPES[tournament_id]

        self.telegram.send_message(f"🚀 Creating {tournament.name}...", chat_id=user_id)

        success, result = self.lichess.create_tournament(
            tournament.full_name,
            tournament.time,
            tournament.increment,
            tournament.variant,
        )

        if success:
            logger.info(f"Tournament created by {username} ({user_id}): {tournament_id}")

            msg = (
                f"🏆 <b>NEW TOURNAMENT!</b> 🏆\n\n"
                f"♟️ <b>Name:</b> {tournament.full_name}\n"
                f"⏱️ <b>Time:</b> {tournament.time}+{tournament.increment}\n"
                f"⏳ Starts in 60 minutes!\n"
                f"👉 Join: {result}"
            )

            self.telegram.send_message(msg, chat_id=TELEGRAM_CHAT_ID)
            self.telegram.send_message("Tournament created! 🏆", chat_id=user_id)

        else:
            self.telegram.send_message(f"❌ Error: {result}", chat_id=user_id)

    @staticmethod
    def _side_to_move(fen: str) -> str:
        """Return 'White' or 'Black' from a FEN string."""
        try:
            color = fen.split(" ")[1]
            return "White" if color == "w" else "Black"
        except (IndexError, AttributeError):
            return "White"

    def _build_puzzle_caption(
        self,
        puzzle_id: str,
        rating: int | str,
        themes: str,
        side: str,
        display_difficulty: str,
        fen: str = "",
    ) -> str:
        """Build the initial puzzle caption (without solution)."""
        link = f"https://lichess.org/training/{puzzle_id}"
        return (
            f"🧩 <b>{display_difficulty} Puzzle</b>\n"
            f"🎯 <b>{side} to move</b>\n"
            f"⭐ <b>Rating:</b> {rating}\n"
            f"🏷️ <b>Themes:</b> {themes}\n\n"
            f"💡 Solution in 4 hours\n\n"
        )

    def _schedule_solution_reveal(
        self, chat_id: int, message_id: int, caption: str, solution: list
    ) -> None:
        """Schedule editing the caption to reveal the solution after 4 hours."""
        solution_str = ", ".join(solution)
        new_caption = caption.replace(
            "💡 Solution in 4 hours",
            f"💡 <b>Solution:</b> <tg-spoiler>{solution_str}</tg-spoiler>",
        )
        timer = threading.Timer(
            14400,
            self.telegram.edit_message_caption,
            args=[chat_id, message_id, new_caption],
        )
        timer.start()
        logger.info(f"Scheduled solution reveal for message {message_id} in 4 hours.")

    def _send_puzzle(self, user_id: int) -> None:
        """Fetch and send a Lichess puzzle to a user in private chat."""
        success, data = self.lichess.get_puzzle()

        if not success:
            self.telegram.send_message("❌ Could not fetch puzzle.", chat_id=user_id)
            return

        puzzle = data.get("puzzle", {})
        difficulty = data.get("custom_difficulty", "normal")

        puzzle_id = puzzle.get("id", "?")
        rating = puzzle.get("rating", "?")
        themes = ", ".join(puzzle.get("themes", [])[:3])
        solution = puzzle.get("solution", [])
        fen = puzzle.get("fen", "")
        side = self._side_to_move(fen)

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

        photo_url = f"https://lichess1.org/training/export/gif/thumbnail/{puzzle_id}.gif?theme={board_theme}"
        caption = self._build_puzzle_caption(puzzle_id, rating, themes, side, display_difficulty,fen)

        sent_success, message_id = self.telegram.send_photo(
            photo_url, caption=caption, chat_id=user_id
        )

        if sent_success and message_id:
            self._schedule_solution_reveal(user_id, message_id, caption, solution)

    def send_scheduled_puzzle(self) -> None:
        """Fetch and send a Lichess puzzle to the group puzzle topic."""
        if not TELEGRAM_PUZZLE_TOPIC_ID:
            logger.error("TELEGRAM_PUZZLE_TOPIC_ID is not set — cannot send scheduled puzzle.")
            return

        success, data = self.lichess.get_puzzle()

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
        side = self._side_to_move(fen)

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

        photo_url = f"https://lichess1.org/training/export/gif/thumbnail/{puzzle_id}.gif?theme={board_theme}"
        caption = self._build_puzzle_caption(puzzle_id, rating, themes, side, display_difficulty,fen)

        sent_success, message_id = self.telegram.send_photo(
            photo_url,
            caption=caption,
            chat_id=TELEGRAM_CHAT_ID,
            topic_id=TELEGRAM_PUZZLE_TOPIC_ID,
        )

        if sent_success and message_id:
            self._schedule_solution_reveal(TELEGRAM_CHAT_ID, message_id, caption, solution)
            logger.info(f"Scheduled puzzle {puzzle_id} sent to group topic {TELEGRAM_PUZZLE_TOPIC_ID}.")
        else:
            logger.error("Scheduled puzzle: failed to send photo to group topic.")