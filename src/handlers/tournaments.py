from src.services import LichessService, TelegramService
from src.config import (
    TOURNAMENT_TYPES,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOURNAMENTS_TOPIC_ID,
    LOG_FILE,
)
from src.utils import Logger

logger = Logger(LOG_FILE)

lichess = LichessService()
telegram = TelegramService()


def create_tournament(
    tournament_id: str,
    username: str,
    user_id: int,
) -> None:
    """Create tournament and notify."""
    tournament = TOURNAMENT_TYPES[tournament_id]

    telegram.send_message(f"🚀 Creating {tournament.name}...", chat_id=user_id)

    success, result = lichess.create_tournament(
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

        telegram.send_message(
            msg,
            chat_id=TELEGRAM_CHAT_ID,
            topic_id=TELEGRAM_TOURNAMENTS_TOPIC_ID,
        )
        telegram.send_message("Tournament created! 🏆", chat_id=user_id)

    else:
        telegram.send_message(f"❌ Error: {result}", chat_id=user_id)
