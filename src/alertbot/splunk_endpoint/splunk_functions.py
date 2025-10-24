from templaters.telegram_templater import TelegramSplunkTemplater
from handlers.telegram_handler import TelegramHandler, TelegramHandlerAPI
from handlers.sms_handler import SMSHandler
from templaters.sms_templater import SMSSplunkTemplater
from alertbot.env import TELEGRAM_MODE, DEFAULT_SENDER
from ..prometheus_endpoint.prom_sms_functions import get_numbers
import logging

logger = logging.getLogger() 

def generate_telegram_splunk_body(keys: list, request_body:list):
    templater = TelegramSplunkTemplater(keys, request_body)
    return templater.get_message()

async def send_telegram_splunk_message(
    message: str, 
    telegram_group_id: str, 
    telegram_topic_id: str = None,
    route_path = "NO_ROUTE"):
    
    telegram_metrics_labels = {
        "cluster": "splunk",
        "severity": "NO_SEVERITY",
        "receiver": route_path
    }
    
    if TELEGRAM_MODE.lower() == "bot":
        logger.info(f"Sending alert splunk to telegram for {message}")
        await TelegramHandler().\
            send_alert_message(chat_id=telegram_group_id, 
                                text=message,
                                message_thread_id=telegram_topic_id)

    elif TELEGRAM_MODE.lower() != "bot":
        logger.info(f"Sending alert splunk to telegram for {message}")
        TelegramHandlerAPI().\
            send_message(chat_id=telegram_group_id,
                        text=message,
                        message_thread_id=telegram_topic_id,
                        telegram_metrics_labels=telegram_metrics_labels)

def generate_sms_splunk_body(keys: list, request_body:list):
    templater = SMSSplunkTemplater(keys, request_body)
    return templater.get_message()

def send_sms_splunk_message(
    message: str,
    keycloak_group_name: str,
    sender: str = DEFAULT_SENDER
):
    numbers = get_numbers([keycloak_group_name])
    sms_handler = SMSHandler()        
    logger.info(f"Sending splunk alert for {numbers}")
    sms_handler.send_sms(
            receptors=numbers,
            message=message,
            sender=sender,
            group=keycloak_group_name,
            cluster="splunk"
        )
    