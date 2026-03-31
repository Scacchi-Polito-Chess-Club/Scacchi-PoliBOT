"""Telegram Bot service."""

from typing import List, Dict, Any, Optional
import requests
from src.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOPIC_ID, LOG_FILE
from src.utils import Logger
from src.models import TelegramSendMessagePayload

logger = Logger(LOG_FILE)


class TelegramService:
    """Send messages via Telegram Bot API."""

    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    def send_message(self, text: str, chat_id: int) -> bool:
        """Send message to chat."""
        payload = TelegramSendMessagePayload(
            chat_id=chat_id,
            message_thread_id=TELEGRAM_TOPIC_ID if chat_id == TELEGRAM_CHAT_ID else None,
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

    def send_keyboard(
        self,
        text: str,
        buttons: List[List[Dict[Any, Any]]],
        chat_id: int,
    ) -> bool:
        """Send message with inline keyboard."""
        payload = TelegramSendMessagePayload(
            chat_id=chat_id,
            text=text,
            message_thread_id=TELEGRAM_TOPIC_ID if chat_id == TELEGRAM_CHAT_ID else None,
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

    def send_photo(
        self,
        photo_url: str,
        caption: str,
        chat_id: int,
        topic_id: Optional[int] = None,
    ) -> tuple[bool, int]:
        """Send a photo with a caption. Returns (success, message_id).

        Args:
            photo_url: URL of the photo to send.
            caption:   HTML caption text.
            chat_id:   Target chat ID.
            topic_id:  Optional topic (message_thread_id) override. When None,
                       falls back to TELEGRAM_TOPIC_ID for the main group chat,
                       or no thread for private chats.
        """
        # Resolve which topic to use:
        #   - explicit topic_id always wins
        #   - fall back to the default TELEGRAM_TOPIC_ID for the main group
        #   - otherwise no thread
        resolved_topic = (
            topic_id
            if topic_id is not None
            else (TELEGRAM_TOPIC_ID if chat_id == TELEGRAM_CHAT_ID else None)
        )

        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML",
        }
        if resolved_topic:
            payload["message_thread_id"] = resolved_topic

        try:
            response = requests.post(
                f"{self.BASE_URL}/sendPhoto",
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                logger.success("Photo sent")
                message_id = response.json().get("result", {}).get("message_id")
                return True, message_id
            else:
                error_msg = response.text[:200]
                logger.error(f"Telegram photo error {response.status_code}: {error_msg}")
                return False, None

        except Exception as e:
            logger.error(f"Exception sending photo: {str(e)[:100]}")
            return False, None

    def edit_message_caption(self, chat_id: int, message_id: int, new_caption: str) -> bool:
        """Edit the caption of an existing message."""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": new_caption,
            "parse_mode": "HTML",
        }
        try:
            response = requests.post(
                f"{self.BASE_URL}/editMessageCaption",
                json=payload,
                timeout=10,
            )
            if response.status_code == 200:
                logger.success(f"Successfully updated message {message_id} with solution")
                return True
            return False
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return False