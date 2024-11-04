from bot.core import TelegramBot
from bot.utils import setup_logging
from config import TELEGRAM_TOKEN, OPENAI_API_KEY, CONFIG_FILE, LOG_LEVEL


def main():
    setup_logging(LOG_LEVEL)

    bot = TelegramBot(
        telegram_token=TELEGRAM_TOKEN,
        openai_api_key=OPENAI_API_KEY,
        config_file=CONFIG_FILE
    )


    bot.run()


if __name__ == '__main__':
    main()