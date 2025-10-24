from kavenegar import KavenegarAPI
from typing import Optional, List
import logging
from utils.retry import retry_on_failure
from utils.metrics import (
    alertbot_sent_sms_per_cluster_counter, 
    alertbot_failed_sent_sms_per_cluster_counter, 
    alertbot_sent_sms_per_number_counter)
from .exceptions import SMSValidationError, SMSSendError

logger = logging.getLogger(__name__)

class SMSHandler:
    _instance = None

    def __new__(cls, api_key: str = None):
        """
        Initialize SMS handler with Kavenegar API key (Singleton)
        
        Args:
            api_key (str): Kavenegar API key
        """
        if cls._instance is None:
            if not api_key:
                raise SMSValidationError("API key cannot be empty")
            cls._instance = super(SMSHandler, cls).__new__(cls)
            instance = cls._instance
            instance.api = KavenegarAPI(api_key)

        return cls._instance
    
    def __init__(self, api_key: str = None):
        # No initialization here, it's all handled in __new__
        # Arguments should be same as __new__ method
        pass

    def _validate_phone_number(self, number: str) -> bool:
        """Validate phone number format"""
        return bool(number and number.isdigit() and len(number) >= 10)

    def _validate_message(self, message: str) -> bool:
        """Validate message content"""
        return bool(message and len(message.strip()) > 0)


    @retry_on_failure()
    def send_sms(self, 
                receptors: List[str], 
                message: str, 
                sender: Optional[str] = None,
                group: Optional[str] = None,
                cluster: Optional[str] = None) -> bool:
        """
        Send bulk SMS to multiple recipients
        
        Args:
            receptors (List[str]): List of recipient phone numbers
            message (str): Message content
            sender (str, optional): Sender number
        
        Returns:
            bool: True if SMS sent successfully
        
        Raises:
            SMSValidationError: If input validation fails
            SMSSendError: If sending fails
        """
        
        alertbot_sent_sms_per_cluster_counter.labels(
            group_name=group,
            cluster=cluster).inc()
        if not receptors:
            raise SMSValidationError("Receptors list cannot be empty")

        for receptor in receptors:
            alertbot_sent_sms_per_number_counter.labels(
                number=receptor,
                group_name=group,
                cluster=cluster
            ).inc()
            if not self._validate_phone_number(receptor):
                raise SMSValidationError(f"Invalid phone number: {receptor}")

        if not self._validate_message(message):
            raise SMSValidationError("Message cannot be empty")

        try:
            self.api.sms_send({
                'receptor': ','.join(receptors),
                'message': message,
                'sender': sender
            })
            logger.info(f"Bulk SMS sent successfully to {len(receptors)} recipients")
            return True
        except Exception as e:
            alertbot_failed_sent_sms_per_cluster_counter.labels(
                group_name=group,
                cluster=cluster).inc()
            logger.error(f"error happened during sending to sms for message: \n {message}")
            logger.error(f"Error sending bulk SMS: {str(e)}")
            raise SMSSendError(f"Failed to send bulk SMS: {str(e)}")