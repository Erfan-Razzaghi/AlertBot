import asyncio, logging
from typing import Dict, Any
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update, error
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes
from alertbot.env import ENABLE_POLLING
class TelegramHandler:
    """
    A Singleton class to handle sending messages to Telegram chats,
    including support for retrying failed messages and handling callback queries.
    """
    _instance = None
    
    def __new__(cls, token: str = None,
                logger: logging.Logger = logging.getLogger(__name__),
                retries: int = 2,
                delay: int = 2):
        
        if cls._instance is None:
            if token is None:
                raise ValueError("Token is required for initialization")
                
            # Create instance
            cls._instance = super(TelegramHandler, cls).__new__(cls)
            
            # Initialize instance (do this only once)
            instance = cls._instance
            instance.token = token
            instance.bot = Bot(token=token)
            instance.app = ApplicationBuilder().token(token).build()
            instance._polling_started = False
            instance.logger = logger
            instance.retries = int(retries)
            instance.delay = int(delay)
            
            if ENABLE_POLLING:
                # Set up the callback query handler
                instance.app.add_handler(CallbackQueryHandler(instance._process_callback))


        return cls._instance

    def __init__(self, token: str = None,
                logger: logging.Logger = logging.getLogger(__name__),
                retries: int = 2,
                delay: int = 2):
        # No initialization here, it's all handled in __new__
        # Arguments should be same as __new__ method
        pass
    
    async def send_message(
        self, 
        chat_id: str, 
        text: str, 
        parse_mode: str = "HTML",
        reply_markup: InlineKeyboardMarkup = None,
        message_thread_id: str = None
    ) -> Dict[str, Any]:
        """
        Send a message to a specific chat.
        
        Args:
            chat_id: Chat ID to send the message to
            text: Message text
            parse_mode: Parse mode (HTML, Markdown, etc.)
            reply_markup: Inline keyboard markup for buttons
            message_thread_id: Thread ID for sending to specific topics
            
        Returns:
            The sent message
        """
        attempt = 0
        while attempt < self.retries:
            try:    
                result = await self.bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    parse_mode=parse_mode, 
                    reply_markup=reply_markup,
                    message_thread_id=message_thread_id
                )
                self.logger.info(f"Successfully sent telegram message after {attempt} retries")
                return result
            except Exception as e:
                attempt += 1
                self.logger.error(f"Failed to send message: attempt {attempt}, {e}")
                self.logger.error(f"Retrying in {self.delay} seconds...")
                await asyncio.sleep(self.delay)
                
        raise error.TelegramError(f"Failed to send message after {self.retries} attempts")
    
    async def send_alert_message(
        self, 
        chat_id: str, 
        text: str, 
        confirm_button_text: str = "💊 Silence",
        parse_mode: str = "HTML",
        message_thread_id: str = None
    ) -> Dict[str, Any]:
        """
        Send an alert message with confirm/cancel buttons.
        
        Args:
            chat_id: Chat ID to send the message to
            text: Alert message text
            confirm_button_text: Text for the confirm button
            cancel_button_text: Text for the cancel button
            parse_mode: Parse mode for the message
            
        Returns:
            The sent message
        """
        # Create simple callback data
        confirm_callback_data = "alert_confirm"
        
        # Create keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton(text=confirm_button_text, callback_data=confirm_callback_data),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the message
        return await self.send_message(chat_id=chat_id, text=text, 
                        parse_mode=parse_mode, reply_markup=reply_markup, 
                        message_thread_id=message_thread_id)

    def polling_error_callback(self, error: error.TelegramError):
        """
        Handles errors that occur during Telegram polling.
        Args:
            error (error.TelegramError): The error that occurred during polling.
        """

        self.logger.error("Telegram polling error!")
        self.logger.error("Error: ", error)
        
    
    async def _process_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process callback queries from button clicks."""
        query = update.callback_query
        callback_data = query.data
        
        # Acknowledge the button click
        await query.answer()
        
        # Handle standard button responses
        if callback_data == "alert_confirm":
            await query.edit_message_text(
                f"{query.message.text}\n\n✅ <b>Silenced</b>", 
                parse_mode="HTML"
            )

    async def setup_polling(self):
        """Set up polling if not already running"""
        if self._polling_started:
            self.logger.info("Polling already started")
            return
            
        self.logger.info("Starting Telegram polling...")
        if not self.app.running:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(allowed_updates=["message", "callback_query"],error_callback=self.polling_error_callback)
            self._polling_started = True
        else:
            self.logger.info("Application is already running")