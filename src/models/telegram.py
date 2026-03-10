"""Telegram API models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TelegramUser(BaseModel):
    """Telegram user information."""

    id: int
    is_bot: bool = False
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram chat information."""

    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None


class TelegramMessage(BaseModel):
    """Incoming Telegram message model."""

    message_id: int
    from_user: TelegramUser = Field(alias="from")
    chat: TelegramChat
    text: Optional[str] = None
    date: int

    model_config = {"populate_by_name": True}


class TelegramCallbackQuery(BaseModel):
    """Telegram callback query model."""

    id: str
    from_user: TelegramUser = Field(alias="from")
    chat_instance: str = Field(alias="chat_instance")
    data: Optional[str] = None

    model_config = {"populate_by_name": True}


class TelegramUpdate(BaseModel):
    """Telegram update wrapper."""

    update_id: int
    message: Optional[TelegramMessage] = None
    callback_query: Optional[TelegramCallbackQuery] = Field(alias="callback_query", default=None)

    model_config = {"populate_by_name": True}


class TelegramSendMessagePayload(BaseModel):
    """Payload for sending Telegram messages."""

    chat_id: int
    text: str
    parse_mode: str = "HTML"
    message_thread_id: Optional[int] = None
    reply_markup: Optional[Dict[Any, Any]] = None


class TelegramInlineButton(BaseModel):
    """Inline keyboard button."""

    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None


class TelegramInlineKeyboard(BaseModel):
    """Inline keyboard markup."""

    inline_keyboard: list[list[TelegramInlineButton]]
