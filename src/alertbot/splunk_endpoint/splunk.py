from fastapi import status, APIRouter, HTTPException, Request
from alertbot.constants import TELEGRAM_CONFIG_WORD, SMS_CONFIG_WORD 
from alertbot.env import ACTIVE_TELEGRAM, ACTIVE_SMS, DEFAULT_SENDER
from .. import globals as globs
from .splunk_functions import (
    generate_telegram_splunk_body,
    generate_sms_splunk_body,
    send_telegram_splunk_message,
    send_sms_splunk_message
)
import logging
import json

router = APIRouter(
    prefix="/api/v2/alerts/splunk",
    tags=["Splunk"]    
)

logger = logging.getLogger()

def find_alert_subtroute(subroute: str):
    if subroute == "":
        return None
    dests = globs.splunk_configs.get("destinations", [])
    logger.debug(f"Looking for a splunk match for subroute {subroute}")
    for dest in dests:
        if dest.get("subroute", "").lower() == subroute:
            return dest
    logger.error(f"No subroute match found for subroute {subroute}!")
    return None

@router.post("/{route_path}", status_code=status.HTTP_204_NO_CONTENT)
async def send_alert(
    route_path: str,
    request: Request
    ):
    logger.info(f"Received Splunk alert on route: /api/v2/alerts/splunk/{route_path}")
    
    # Get the body content
    body = await request.body()
    
    try:
        body_dict = json.loads(body.decode('utf-8')) if body else {}
    except json.JSONDecodeError:
        body_dict = {"raw_body": body.decode('utf-8') if body else 'Empty body'}

    dest = find_alert_subtroute(route_path)
    if not dest:
        logger.warning(f"Route {route_path} is not configured in Splunk.")
        logger.warning(f"here is the body of the message received for better troubleshooting: ")
        logger.warning(f"{body_dict}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Route {route_path} not found.")

    for types in dest.get("types", []):
        if types.get("type") == TELEGRAM_CONFIG_WORD:
            message = generate_telegram_splunk_body(dest["keys"], body_dict)
            logger.debug(f"Generated Telegram message: {message}")
            if ACTIVE_TELEGRAM:
                await send_telegram_splunk_message(
                    message, 
                    types["telegram_group_id"], 
                    types.get("telegram_topic_id", None),
                    route_path
                    )
            else:
                logger.error("Telegram is not active to send telegram alert.")

        elif types.get("type") == SMS_CONFIG_WORD:
            message = generate_sms_splunk_body(dest["keys"], body_dict)
            logger.info(f"Generated SMS message: {message}")
            if ACTIVE_SMS:
                send_sms_splunk_message(
                    message,
                    types["keycloak_group_name"],
                    types.get("sender", DEFAULT_SENDER)
                )
            else:
                logger.error("SMS is not active to send SMS alert.")