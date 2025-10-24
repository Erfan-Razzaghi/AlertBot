from templaters.telegram_templater import TelegramTemplater
from handlers.telegram_handler import TelegramHandler, TelegramHandlerAPI
from alertbot.schemas import AlertRequestPrometheus
from .. import globals as globs
from alertbot.env import TELEGRAM_MODE
import logging


logger = logging.getLogger()

def find_alert_receiver(alert: AlertRequestPrometheus):
    logger.debug(f"Looking for a match for receiver {alert.receiver}")
    for dest in globs.configs["destinations"]:
        if dest["receiver"].lower() ==  alert.receiver and \
           dest["severity"] in alert.alerts[0].labels["severity"].lower():
            return dest
    logger.error(f"No receiver match found for receiver {alert.receiver}!")
    return None

async def generate_send_telegram_alert(
        alert: AlertRequestPrometheus,
        target: dict):
    """
    Generate and send a Telegram alert message for a Prometheus alert.
    This function will:
    1. Instantiate a TelegramTemplater to format the alert text.
    2. Choose between two send methods depending on whether a “silencer” button is requested and send message: 
       - `send_alert_message` (with silencer)
       - `send_message` (plain text)
    Args:
        alert (AlertRequestPrometheus):
            The Prometheus alert request object containing metadata like `receiver`.
        target (dict):
            Configuration for where and how to send:
              - "telegram_group_id" (str): Telegram chat ID to deliver the alert.
              - "silencer" (bool, optional): If True, include a silencer button via `send_alert_message`.
                                         Defaults to False.
    Returns:
        None
    """
    telegram_templater = TelegramTemplater(alert_group = alert)
    silencer_active = target.get("silencer", False)
    telegram_metrics_labels = {
        "receiver": alert.receiver,
        "cluster": telegram_templater.get_cluster(),
        "severity": telegram_templater.get_severity()
    }
    logger.info("generated alert message for telegram successfully!")

    logger.debug(telegram_templater.get_message())
    if TELEGRAM_MODE.lower() == "bot" and silencer_active:
        logger.info(f"Sending alert telegram for {alert.receiver} with silencer button...")
        await TelegramHandler().\
            send_alert_message(chat_id=target["telegram_group_id"], 
                                text=telegram_templater.get_message(),
                                message_thread_id=target.get("telegram_topic_id", None))
            
    elif TELEGRAM_MODE.lower() != "bot":
        if silencer_active:
            logger.warning(f"Sending alert telegram for {alert.receiver} is being sent via API because TELEGRAM_MODE is not 'bot'")
        logger.info(f"Sending alert telegram for {alert.receiver} without silencer button...")
        TelegramHandlerAPI().\
            send_message(chat_id=target["telegram_group_id"],
                        text=telegram_templater.get_message(),
                        message_thread_id=target.get("telegram_topic_id", None),
                        telegram_metrics_labels=telegram_metrics_labels)