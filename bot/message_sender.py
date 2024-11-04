from typing import Set, Optional
import logging
from telegram import Bot, ReplyKeyboardMarkup
from telegram.error import TelegramError


class MessageSender:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_chats: Set[int] = set()

    async def send_message(
            self,
            chat_id: int,
            text: str,
            reply_markup: Optional[ReplyKeyboardMarkup] = None
    ) -> bool:
        """
        Send a message to a specific chat

        Args:
            chat_id (int): The ID of the chat to send the message to
            text (str): The text message to send
            reply_markup (Optional[ReplyKeyboardMarkup]): Optional keyboard markup for the message

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
            return True
        except TelegramError as e:
            logging.error(f"Failed to send message to {chat_id}: {e}")
            if "Forbidden" in str(e):
                self.active_chats.discard(chat_id)
            return False
