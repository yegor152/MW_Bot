import pandas as pd
from typing import Dict, Any
import logging


class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.instructions: Dict[str, str] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from Excel file"""
        try:
            messages_df = pd.read_excel(self.config_file)
            self.instructions = dict(zip(messages_df.iloc[:, 0], messages_df.iloc[:, 1]))

        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise



