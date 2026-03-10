"""Lichess API service."""

from datetime import datetime, timedelta
import sys
import requests
from src.config import LICHESS_TOKEN, TEAM_ID, LOG_FILE
from src.utils import Logger
from src.models import TournamentPayload

logger = Logger(LOG_FILE)


class LichessService:
    """Create tournaments on Lichess."""

    BASE_URL = "https://lichess.org/api"

    def __init__(self):
        self.headers = {"Authorization": f"Bearer {LICHESS_TOKEN}"}

    def create_tournament(
        self,
        name: str,
        time: int,
        increment: int,
        variant: str,
    ) -> tuple[bool, str]:
        """Create a tournament on Lichess."""
        if not TEAM_ID:
            logger.error("Missing environment variable TEAM_ID")
            sys.exit(1)

        start_date = datetime.now() + timedelta(minutes=60)

        payload = TournamentPayload(
            name=name,
            clock_time=time,
            clock_increment=increment,
            variant=variant,
            minutes=60,
            team_id=TEAM_ID,
            start_date=int(start_date.timestamp() * 1000),
        ).to_lichess_payload()

        try:
            logger.info(f"Creating tournament: {name}")

            response = requests.post(
                f"{self.BASE_URL}/tournament",
                headers=self.headers,
                data=payload,
                timeout=30,
            )

            logger.debug(f"Lichess response: {response.status_code}")

            if response.status_code == 200:
                tournament_id = response.json()["id"]
                link = f"https://lichess.org/tournament/{tournament_id}"
                logger.success(f"Tournament created: {tournament_id}")
                return True, link

            elif response.status_code == 401:
                logger.error("Invalid Lichess token")
                return False, "Invalid Lichess token"

            elif response.status_code == 403:
                logger.error("Insufficient permissions")
                return False, "Insufficient permissions"

            elif response.status_code == 400:
                error = response.json().get("error", "Bad request")
                logger.error(f"Bad request: {error}")
                return False, error

            else:
                logger.error(f"Lichess error {response.status_code}")
                return False, f"Error: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error("Lichess timeout")
            return False, "Lichess timeout"

        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return False, "Connection error"

        except Exception as e:
            logger.error(f"Exception: {str(e)[:100]}")
            return False, str(e)[:100]
