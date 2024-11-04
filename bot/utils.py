import logging



def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the bot"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, level)
    )



