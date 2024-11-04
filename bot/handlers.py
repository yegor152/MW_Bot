import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes


class MessageHandlers:
    def __init__(self, message_sender, chatgpt_client, config_manager, user_manager):
        self.message_sender = message_sender
        self.chatgpt_client = chatgpt_client
        self.config_manager = config_manager
        self.user_manager = user_manager

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command"""
        chat_id = update.effective_chat.id
        username = update.message.from_user.username if update.message.from_user else None

        # Initialize user in database
        self.user_manager.initialize_user(chat_id, username)

        # Check if user already has complete profile
        if self.user_manager.has_complete_profile(chat_id):
            # If profile is complete, don't show the contact button
            await self.message_sender.send_message(
                chat_id,
                self.config_manager.instructions["welcome"],
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            # Show contact request button for incomplete profiles
            keyboard = [[KeyboardButton(self.config_manager.instructions["btn_text"], request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await self.message_sender.send_message(
                chat_id,
                self.config_manager.instructions["welcome"],
                reply_markup=reply_markup
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages and contacts"""
        chat_id = update.effective_chat.id

        # Handle contact sharing
        if update.message.contact:
            phone = update.message.contact.phone_number
            name = update.message.contact.first_name

            # Update user info
            success = self.user_manager.update_user_info(
                chat_id=chat_id,
                name=name,
                phone=phone
            )

            if success:
                # Get admin chat ID from config
                admin_chat_id = self.config_manager.instructions.get("admin_chat_id")

                if admin_chat_id:
                    # Get user details for admin notification
                    user_details = self.user_manager.get_user_details(chat_id)

                    if user_details:
                        # Format admin notification message
                        admin_message = (
                            f"🆕 New User Registration:\n"
                            f"Name: {user_details['name']}\n"
                            f"Phone: {user_details['phone']}\n"
                            f"Username: @{user_details['username'] or 'Not provided'}\n"
                            f"Registration Date: {user_details['registration_date']}"
                        )

                        try:
                            # Send notification to admin
                            await self.message_sender.send_message(
                                int(admin_chat_id),
                                admin_message
                            )
                        except Exception as e:
                            logging.error(f"Failed to send admin notification: {e}")

                thank_you_message = self.config_manager.instructions["contact_received"]
                # Send thank you message with explicit keyboard removal
                await self.message_sender.send_message(
                    chat_id,
                    thank_you_message,
                    reply_markup=ReplyKeyboardRemove()
                )
            return

        # For text messages
        if update.message.text:
            # Check if user has shared contact information
            if not self.user_manager.has_complete_profile(chat_id):
                # Create keyboard with contact request button
                keyboard = [[KeyboardButton(self.config_manager.instructions["btn_text"], request_contact=True)]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

                access_denied_message = self.config_manager.instructions["access_denied"]

                await self.message_sender.send_message(
                    chat_id,
                    access_denied_message,
                    reply_markup=reply_markup
                )
                return

            # Process message with ChatGPT
            response = await self.chatgpt_client.get_response(
                chat_id,
                update.message.text,
            )
            # Send response without any keyboard
            await self.message_sender.send_message(
                chat_id,
                response,
                reply_markup=ReplyKeyboardRemove()
            )