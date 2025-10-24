
from templaters.sms_templater import SMSTemplater
from handlers.sms_handler import SMSHandler
from alertbot.schemas import AlertRequestPrometheus
from alertbot.env import PHONE_SYNC_API_URL, PHONE_SYNC_API_ROUTE, \
    LIMIT_SMS_NUMBER_PER_ALERT_GROUP, DEFAULT_SENDER
from alertbot.constants import SMS_LIMIT_ERROR_MESSAGE
from utils.make_api_call import make_api_call
from utils.metrics import alertbot_keycloak_group_members
import logging
import json

logger = logging.getLogger(__name__)

def generate_send_sms_alert(
        alert_group: AlertRequestPrometheus,
        target: dict):
    """
    Generate SMS messages for a Prometheus alert group and send them to the configured recipients.

    This function will:
    1. Look up phone numbers for the given `target["keycloak_group_name"]`.
    2. Build SMS message bodies using `SMSTemplater`.
    3. Send each message via `SMSHandler`, up to a maximum of `LIMIT_SMS_NUMBER_PER_ALERT_GROUP`.
       If there are more messages than the limit, a warning message will be sent indicating how many
       messages were suppressed.

    Any errors during number lookup, message templating, or sending are caught and logged; in those
    cases the function returns early without raising.

    Args:
        alert_group (AlertRequestPrometheus):
            The Prometheus alert group for which SMS notifications should be generated.
        target (dict):
            A dictionary containing:
              - "keycloak_group_name" (str): the name of the Keycloak group whose members should receive the SMS.
              - "sender" (optional, str): the SMS sender ID to use; falls back to DEFAULT_SENDER.

    Returns:
        None
    """
    group=target["keycloak_group_name"]
    numbers = get_numbers([group])
    alertbot_keycloak_group_members.labels(group_name=group).set(len(numbers))

    
    logger.info(f"got numbers {numbers} for receiver {[group]}")

    sms_templater = SMSTemplater(alert_group)
    
    messages = sms_templater.get_messages()
    cluster = sms_templater.get_cluster_name()
    limit_reached = False
    logger.info(f"generated messages for sms: {messages}")
    
    sms_handler = SMSHandler()
    for message_count, message in enumerate(messages):
        if message_count == LIMIT_SMS_NUMBER_PER_ALERT_GROUP:
            limit_reached = True
            message = generate_limit_message(int(len(messages) - message_count), 
                                                    sms_templater.get_alert_name())
        sms_handler.send_sms(
            receptors=numbers,
            message=message,
            sender=target.get("sender", DEFAULT_SENDER),
            group=group,
            cluster=cluster
        )
        if limit_reached:
            break


def get_numbers(receivers):
    """
    Fetches phone numbers from the phone synchronization API for the given receivers.
    Args:
        receivers (list): A list of receiver identifiers for which phone numbers are to be fetched.
    Returns:
        dict: A dictionary containing the fetched phone numbers or an error message if the request fails.
    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request to the phone synchronization API.
    """
    result = []
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
    }
    body = json.dumps({
        "receivers": receivers
    })
    logger.info(f"Calling Phone Sync API for receivers {receivers}")
    response = make_api_call(
        method="GET",
        url=PHONE_SYNC_API_URL + PHONE_SYNC_API_ROUTE,
        headers=headers,
        payload = body,
        retry_count = 3
    )

    # Raise an Error for 4xx and 5xx
    response.raise_for_status()
    
    logger.info(f"Calling Phone Sync API Done {response.status_code}")
    logger.debug(f"Respone body is as followed: {response.json()}")

    result = create_numbers_list(response.json())

    #Removing all the invalid numbers with length less than 10
    result_filtered = [number for number in result if len(number)>=10]
    return result_filtered
    

def create_numbers_list(response_json: dict = {}):
    """
    Gets a dictionary returned by phone sync api like this 
    {
        'sre-critical': '09120067808,09103936034,09372598219,09356388553,09364226811,09195929407', 
        'critical': '09103936034'
    }
    and returns a list of all unique numbers mentioned in this dictionary values
    Args:
        response (dict): a dictionary returned by phone sync api
    Returns:
        list: A list of all numbers uniquely.
    """
    result_str = ""
    santized_line = ""
    for each_calling_list in response_json.values():
        if len(each_calling_list) < 10:
            # This means that the value does not have any numbers in it
            continue
        santized_line = each_calling_list            
        santized_line = santized_line.replace("\"", "")
        santized_line = santized_line.replace("'", "")
        result_str = result_str + "," + santized_line
    
    return list(set(result_str.split(","))) # Don't return one repeatative number twice

def generate_limit_message(num: int, alertname: str) -> str:
    return SMS_LIMIT_ERROR_MESSAGE.\
        replace(
        "##NUMBER##",str(num)
        ).\
        replace(
        "##ALERTNAME##", alertname
        )