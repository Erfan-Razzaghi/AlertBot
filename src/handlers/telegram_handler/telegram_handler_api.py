from utils.make_api_call import make_api_call
from utils.metrics import (
    alertbot_sent_telegram_per_receiver_counter, 
    alertbot_failed_sent_telegram_per_receiver_counter
)
from alertbot.constants import TELEGRAM_MAX_MESSAGE_LENGTH
from time import sleep
from telegram import error
import logging

class TelegramHandlerAPI:
    """
    A Singleton class to handle sending messages to Telegram chats using only API's
    """
    _instance = None

    def __new__(cls, token: str = None,
                logger: logging.Logger = logging.getLogger(__name__),
                retries: int = 2,
                delay: int = 2):
        
        if cls._instance is None:
            if token is None:
                raise ValueError("Token is required for initialization of telegram handler API")
                
            # Create instance
            cls._instance = super(TelegramHandlerAPI, cls).__new__(cls)
            
            # Initialize instance (do this only once)
            instance = cls._instance
            instance.token = token
            instance.logger = logger
            instance.retries = int(retries)
            instance.delay = int(delay)

        return cls._instance
    
    def __init__(self, token: str = None,
                logger: logging.Logger = logging.getLogger(__name__),
                retries: int = 2,
                delay: int = 2):
        # No initialization here, it's all handled in __new__
        # Arguments should be same as __new__ method
        pass


    def send_message(self, chat_id: str, 
                     text: str = "Empty Text",
                     parse_mode: str = "HTML",
                     message_thread_id: str = None,
                     telegram_metrics_labels: dict = {}):
        self.logger.debug(f"Message size is: {len(text)}")
        
        # Check if message exceeds maximum length and split if necessary
        if len(text) > TELEGRAM_MAX_MESSAGE_LENGTH:
            self.logger.info(f"Message size {len(text)} exceeds limit {TELEGRAM_MAX_MESSAGE_LENGTH}. Splitting message.")
            text_chunks = self._split_message(text, TELEGRAM_MAX_MESSAGE_LENGTH)
            
            # Send each chunk as a separate message
            for i, chunk in enumerate(text_chunks):
                self.logger.info(f"Sending message chunk {i + 1}/{len(text_chunks)}")
                self._send_single_message(chat_id, chunk, parse_mode, message_thread_id, telegram_metrics_labels)
        else:
            # Send single message
            self._send_single_message(chat_id, text, parse_mode, message_thread_id, telegram_metrics_labels)

    def _split_message(self, text: str, max_length: int):
        """Split a message into chunks that don't exceed max_length"""
        chunks = []
        while len(text) > max_length:
            # Find a good breaking point (newline, space, or period)
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:
                split_pos = text.rfind(' ', 0, max_length)
            if split_pos == -1:
                split_pos = text.rfind('.', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
            
            chunks.append(text[:split_pos])
            text = text[split_pos:].lstrip()
        
        if text:
            chunks.append(text)
        return chunks

    def _send_single_message(self, chat_id: str, text: str, parse_mode: str, message_thread_id: str = None, 
                             telegram_metrics_labels: dict = {}):
        """Send a single message to Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": "true"
        }
        
        # Add message_thread_id if provided (for sending to specific topics)
        if message_thread_id:
            data["message_thread_id"] = message_thread_id

        for i in range(self.retries):
            self.logger.info(
            f"Calling Telegram API for Chat ID {chat_id} "
            )
            response = make_api_call(method="POST", 
                                    url=url,
                                    payload=data)
            if response is not None and response.status_code < 300 and response.status_code >= 200:
                self.logger.info(f"Successfully sent message for telegram. Status code: {response.status_code}")
                alertbot_sent_telegram_per_receiver_counter.labels(
                    **telegram_metrics_labels
                ).inc()
            else: # Sth is wrong, we haven't got 2XX status code
                if response is not None:
                    self.logger.error(f"Failed to send message {text}. Status code: " +
                                    f"{response.status_code}, Response text: {response.text}")
                else:
                    self.logger.error("No response was received!")
                if i != self.retries - 1:
                    self.logger.error(f"sleeping for {self.delay} after retry number {i + 1}")
                    sleep(self.delay)

                else: 
                    alertbot_failed_sent_telegram_per_receiver_counter.labels(
                        **telegram_metrics_labels
                    ).inc()
                    raise error.TelegramError(f"Failed to send message after {self.retries} attempts")
                continue
            break
