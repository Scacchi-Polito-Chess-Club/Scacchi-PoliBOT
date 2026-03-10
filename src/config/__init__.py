"""Configuration module."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
TELEGRAM_TOPIC_ID = int(os.getenv("TELEGRAM_TOPIC_ID", "0"))

# Lichess
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
TEAM_ID = os.getenv("TEAM_ID")

# Authorized users
AUTHORIZED_USERS = {
    652283475,  # Filippo
    1163968938,  # Leonardo
}

# Tournament types - using Pydantic model
from src.models import TournamentType

TOURNAMENT_TYPES: dict[str, TournamentType] = {
    "bullet10": TournamentType(
        name="1+0 Bullet",
        cmd="/bullet",
        time=1,
        increment=0,
        variant="standard",
        full_name="Scacchi PoliTO - 1+0 Bullet",
    ),
    "blitz21": TournamentType(
        name="2+1 Blitz",
        cmd="/blitz",
        time=2,
        increment=1,
        variant="standard",
        full_name="Scacchi PoliTO - 2+1 Blitz",
    ),
    "chess960": TournamentType(
        name="3+2 Chess960",
        cmd="/chess960",
        time=3,
        increment=2,
        variant="chess960",
        full_name="Scacchi PoliTO - 3+2 Chess960",
    ),
}

COMMANDS = {v.cmd: k for k, v in TOURNAMENT_TYPES.items()}
