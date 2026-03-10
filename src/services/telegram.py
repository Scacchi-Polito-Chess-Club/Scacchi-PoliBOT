"""Telegram Bot service."""

from typing import List, Dict, Any
import requests
from src.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOPIC_ID, LOG_FILE
from src.utils import Logger
from src.models import TelegramSendMessagePayload

logger = Logger(LOG_FILE)


class TelegramService:
    """Send messages via Telegram Bot API."""

    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    def send_message(self, text: str) -> bool:
        """Send message to chat."""
        payload = TelegramSendMessagePayload(
            chat_id=TELEGRAM_CHAT_ID,
            message_thread_id=TELEGRAM_TOPIC_ID,
            text=text,
        )

        try:
            response = requests.post(
                f"{self.BASE_URL}/sendMessage",
                json=payload.model_dump(exclude_none=True),
                timeout=10,
            )

            logger.debug(f"Telegram response: {response.status_code}")

            if response.status_code == 200:
                logger.success("Message sent")
                return True
            else:
                error_msg = response.text[:200]
                logger.error(f"Telegram error {response.status_code}: {error_msg}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Telegram timeout")
            return False
        except Exception as e:
            logger.error(f"Exception: {str(e)[:100]}")
            return False

    def send_keyboard(self, text: str, buttons: List[List[Dict[Any, Any]]]) -> bool:
        """Send message with inline keyboard."""
        payload = TelegramSendMessagePayload(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            message_thread_id=TELEGRAM_TOPIC_ID,
            reply_markup={"inline_keyboard": buttons},
        )

        try:
            response = requests.post(
                f"{self.BASE_URL}/sendMessage",
                json=payload.model_dump(exclude_none=True),
                timeout=10,
            )

            if response.status_code == 200:
                logger.success("Keyboard message sent")
                return True
            else:
                logger.error(f"Telegram error: {response.text[:200]}")
                return False

        except Exception as e:
            logger.error(f"Exception: {str(e)[:100]}")
            return False
