from fastapi import status, APIRouter, HTTPException
from alertbot.schemas import AlertRequestPrometheus
from alertbot.constants import TELEGRAM_CONFIG_WORD, SMS_CONFIG_WORD 
from alertbot.prometheus_endpoint.prom_telegram_functions import find_alert_receiver, \
    generate_send_telegram_alert
from alertbot.env import ACTIVE_TELEGRAM, ACTIVE_SMS
from alertbot.prometheus_endpoint.prom_sms_functions import generate_send_sms_alert
import logging

router = APIRouter(
    prefix="/api/v2/alerts/prom",
    tags=["Promethues"]    
)

logger = logging.getLogger()


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def send_alert(
    new_alert: AlertRequestPrometheus
    ):

    logger.info("/api/v2/alerts/prom endpoint has been called...")
    dest = find_alert_receiver(new_alert)
    logger.debug(f"{new_alert}")
    if dest is None:
        logger.error(f"No match found for the given receiver!")
        logger.error(f"alert request: {new_alert}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="No destination was found for this alert!")
    
    logger.info(f"receiver match found for {new_alert.receiver}")

    for target in dest["types"]:
        if TELEGRAM_CONFIG_WORD in target["type"].lower():
            logger.info("Generating telegram alert...")
            if ACTIVE_TELEGRAM:
                await generate_send_telegram_alert(
                    alert=new_alert,
                    target=target)
            else:
                logger.error(f"ACTIVE_TELEGRAM env is not set! the alert for " + 
                f"receiver {new_alert.receiver} will not be sent to telegram!")

        elif SMS_CONFIG_WORD in target["type"].lower(): 
            logger.info("Generating sms alert...")
            if ACTIVE_SMS:
                generate_send_sms_alert(
                    alert_group=new_alert,
                    target=target
                )   
            else:
                logger.error(f"ACTIVE_SMS env is not set! the alert for " + 
                f"receiver {new_alert.receiver} will not be sent to SMS!")

    return 