from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .handlers import MessageHandlers
from .message_sender import MessageSender
from .chatgpt_client import ChatGPTClient
from .config_manager import ConfigManager
from .user_manager import UserManager


class TelegramBot:
    def __init__(
            self,
            telegram_token: str,
            openai_api_key: str,
            config_file: str
    ):
        """Initialize the bot with all components"""
        self.app = Application.builder().token(telegram_token).build()
        self.config_manager = ConfigManager(config_file)
        self.message_sender = MessageSender(self.app.bot)
        self.chatgpt_client = ChatGPTClient(openai_api_key, self.config_manager)
        self.user_manager = UserManager()
        self.handlers = MessageHandlers(
            self.message_sender,
            self.chatgpt_client,
            self.config_manager,
            self.user_manager
        )

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up all message handlers"""
        # Command handler for /start
        self.app.add_handler(CommandHandler("start", self.handlers.start_command))

        # Contact message handler
        self.app.add_handler(MessageHandler(
            filters.CONTACT,
            self.handlers.handle_message
        ))

        # Text message handler (excluding commands)
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handlers.handle_message
        ))

    def run(self) -> None:
        """Run the bot"""
        self.app.run_polling()