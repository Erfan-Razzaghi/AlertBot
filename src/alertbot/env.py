import os

from dotenv import load_dotenv
from .constants import CONFIGS_DIRECTORY

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO") 
ENVIRONMENT = os.environ.get("ENVIRONMENT", "STAGING")
TIMEZONE = os.environ.get("TZ", "Asia/Tehran")
CONFIG_JSON_FILE = CONFIGS_DIRECTORY + os.environ.get("CONFIG_JSON_FILE", "alertbot-config.json")
CONFIG_SPLUNK_JSON_FILE = CONFIGS_DIRECTORY + os.environ.get("CONFIG_SPLUNK_JSON_FILE", "alertbot-splunk-config.json")
CONFIG_RELOADER_INTERVAL = int(os.environ.get("CONFIG_RELOADER_INTERVAL", "60"))

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_SEND_RETRIES = os.environ.get("TG_SEND_RETRIES", "3")
TG_SEND_RETRY_DELAY = os.environ.get("TG_SEND_RETRY_DELAY", "5")
TG_GROUP_TEST_ID = os.environ.get("TG_GROUP_TEST", "")
ACTIVE_TELEGRAM=False
TELEGRAM_MODE = os.environ.get("TELEGRAM_MODE", "API") # it is either API or BOT
ENABLE_POLLING = False
if "true" in os.environ.get("ENABLE_POLLING", "true").lower():
    ENABLE_POLLING = True
if "true" in os.environ.get("ACTIVE_TELEGRAM", "true").lower():
    ACTIVE_TELEGRAM = True


KAVENEGAR_API_KEY = os.environ.get("KAVENEGAR_API_KEY", "")
PHONE_SYNC_API_URL = os.environ.get("PHONE_SYNC_API_URL", "http://localhost:8001")
PHONE_SYNC_API_ROUTE = os.environ.get("PHONE_SYNC_API_ROUTE", "/api/numbers")
DEFAULT_SENDER = os.environ.get("DEFAULT_SENDER", "100008700")
LIMIT_SMS_NUMBER_PER_ALERT_GROUP = int(os.environ.get("LIMIT_SMS_NUMBER_PER_ALERT_GROUP", 2))
ACTIVE_SMS=False
if "true" in os.environ.get("ACTIVE_SMS", "true").lower():
    ACTIVE_SMS = True

