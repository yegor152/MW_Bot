from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
from .config_manager import ConfigManager


class ChatGPTClient:
    def __init__(self, oai_api_key: str, config_manager: ConfigManager):
        """
        Initialize ChatGPT client

        Args:
            oai_api_key (str): OpenAI API key
            config_manager (ConfigManager): Instance of ConfigManager for accessing prompts
        """
        self.client = OpenAI(api_key=oai_api_key)
        self.config_manager = config_manager
        self.conversations: Dict[int, List[Dict[str, str]]] = {}

    async def get_response(
            self,
            chat_id: int,
            user_message: str,
    ) -> str:
        """
        Get response from ChatGPT

        Args:
            chat_id (int): Telegram chat ID
            user_message (str): User's message
            prompt_key (str): Key for selecting system prompt from config

        Returns:
            str: ChatGPT's response
        """
        try:
            # Get system prompt from config
            system_prompt = self.config_manager.instructions['prompt']

            # Initialize or update conversation with new system prompt
            if chat_id not in self.conversations:
                self.conversations[chat_id] = []

            # If conversation exists but system prompt is different, reset conversation
            if self.conversations[chat_id]:
                current_system_prompt = self.conversations[chat_id][0]["content"]
                if current_system_prompt != system_prompt:
                    self.conversations[chat_id] = []

            # Add system prompt if it's a new conversation
            if not self.conversations[chat_id]:
                self.conversations[chat_id].append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add user message
            self.conversations[chat_id].append({
                "role": "user",
                "content": user_message
            })

            # Keep conversation history limited
            # Keep system prompt and last 4 exchanges (8 messages: 4 user + 4 assistant)
            if len(self.conversations[chat_id]) > 9:  # system prompt + 8 messages
                self.conversations[chat_id] = (
                        [self.conversations[chat_id][0]] +  # Keep system prompt
                        self.conversations[chat_id][-8:]  # Keep last 8 messages
                )

            # Get response from ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversations[chat_id],
                max_tokens=700,
                temperature=0.7,  # Add some variability to responses
                presence_penalty=0.7,  # Encourage new topics
                frequency_penalty=0.6  # Reduce repetition
            )

            # Extract and store response
            assistant_message = response.choices[0].message.content
            self.conversations[chat_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            logging.error(f"Error getting ChatGPT response: {e}")
            return "I apologize, but I'm having trouble processing your request right now."

    def reset_conversation(self, chat_id: int) -> None:
        """
        Reset conversation history for a specific chat

        Args:
            chat_id (int): Telegram chat ID to reset
        """
        if chat_id in self.conversations:
            self.conversations.pop(chat_id)

    def get_conversation_history(self, chat_id: int) -> Optional[List[Dict[str, str]]]:
        """
        Get conversation history for a specific chat

        Args:
            chat_id (int): Telegram chat ID

        Returns:
            Optional[List[Dict[str, str]]]: Conversation history or None if not found
        """
        return self.conversations.get(chat_id)

    def change_system_prompt(self, chat_id: int, prompt_key: str) -> bool:
        """
        Change system prompt for a specific chat

        Args:
            chat_id (int): Telegram chat ID
            prompt_key (str): Key for selecting new system prompt from config

        Returns:
            bool: True if prompt was changed successfully
        """
        try:
            new_system_prompt = self.config_manager.get_system_prompt(prompt_key)
            if not new_system_prompt:
                return False

            # Reset conversation and add new system prompt
            self.reset_conversation(chat_id)
            self.conversations[chat_id] = [{
                "role": "system",
                "content": new_system_prompt
            }]
            return True
        except Exception as e:
            logging.error(f"Error changing system prompt: {e}")
            return False