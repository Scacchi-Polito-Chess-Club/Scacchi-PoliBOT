"""Handle Telegram messages and callbacks."""

from typing import Dict, Any
from src.config import (
    AUTHORIZED_USERS,
    TOURNAMENTS_COMMANDS,
    TOURNAMENTS_KEYBOARD,
    LOG_FILE,
)
from src.services import LichessService, TelegramService
from src.utils import Logger
from .tournaments import create_tournament
from .puzzles import send_puzzle


logger = Logger(LOG_FILE)


class MessageHandler:
    """Process incoming Telegram messages."""

    def __init__(self):
        self.lichess = LichessService()
        self.telegram = TelegramService()

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        return user_id in AUTHORIZED_USERS

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

        if text == "/help":
            self.telegram.send_message(
                "/tournaments - Tournaments overview\n/bullet - 1+0 Bullet\n/blitz - 2+1 Blitz\n/chess960 - 3+2 Chess960\n/puzzle - Puzzle",
                chat_id=user_id,
            )

        elif text == "/tournaments":
            self.telegram.send_keyboard(
                "🏆 <b>Lichess Tournament Manager</b>\n\nSelect tournament type:",
                TOURNAMENTS_KEYBOARD,
                chat_id=user_id,
            )

        elif text == "/puzzle":
            send_puzzle(user_id)

        elif text in TOURNAMENTS_COMMANDS:
            tournament_id = TOURNAMENTS_COMMANDS[text]
            create_tournament(tournament_id, username, user_id)

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
            create_tournament(tournament_id, username, user_id)
