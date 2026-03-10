"""Handle Telegram messages and callbacks."""

from typing import Dict, List, Any
from src.config import AUTHORIZED_USERS, TOURNAMENT_TYPES, COMMANDS, LOG_FILE, TELEGRAM_CHAT_ID
from src.services import LichessService, TelegramService
from src.utils import Logger

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
        chat_id = message.get("chat", {}).get("id")

        if not self.is_authorized(user_id):
            self.telegram.send_message("❌ Not authorized", chat_id=chat_id)
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
                "/start - Menu\n/bullet - 1+0 Bullet\n/blitz - 2+1 Blitz\n/chess960 - 3+2 Chess960",
                chat_id=user_id,
            )

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
