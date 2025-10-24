from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from alertbot.env import (
    TG_BOT_TOKEN, TG_SEND_RETRIES, 
    TG_SEND_RETRY_DELAY, ACTIVE_TELEGRAM, 
    KAVENEGAR_API_KEY, ACTIVE_SMS, TELEGRAM_MODE,
    TIMEZONE, CONFIG_RELOADER_INTERVAL)
from alertbot.alertbot_config_manager import ConfigManager
from handlers.telegram_handler import TelegramHandler, TelegramHandlerAPI
from handlers.sms_handler import SMSHandler
import logging
import alertbot.globals as globs

logger = logging.getLogger(__name__)

def refresh_config():
    "Reload Configuration From File"
    config_manager = ConfigManager()
    config_manager.read_alertbot_configs()
    config_manager.read_alertbot_splunk_configs()
    globs.configs = config_manager.get_alertbot_config()
    globs.splunk_configs = config_manager.get_alertbot_splunk_config()

def setup_job_config_reloader():
    logger.info("Setting up auto-reloader...")
    scheduler = BackgroundScheduler(timezone=timezone(TIMEZONE))

    # Add config reload job every 5 seconds
    scheduler.add_job(
        refresh_config,
        'interval',
        seconds=CONFIG_RELOADER_INTERVAL,
        max_instances=1,
        id='config_reload',
        timezone=TIMEZONE 
    )

    scheduler.start()
    refresh_config()  # Initial config load

async def setup_telegram_bot(logger):
    try:
        logger.info("Starting telegram bot")
        bot = TelegramHandler(TG_BOT_TOKEN, retries=TG_SEND_RETRIES, delay=TG_SEND_RETRY_DELAY)
        await bot.setup_polling()
    except Exception as e:
        logger.error("Failed to setup Telegram bot")
        logger.error("Error: ", e)

def setup_telegram_api(logger):
    try:
        TelegramHandlerAPI(token=TG_BOT_TOKEN, retries=TG_SEND_RETRIES, delay=TG_SEND_RETRY_DELAY)
    except Exception as e:
        logger.error("Failed to setup Telegram api")
        logger.error("Error: ", e)

@asynccontextmanager
async def lifespan(app):
    # Starting up code
    logger.info("Application's logger started, Starting application...")
    setup_job_config_reloader()
    
    if ACTIVE_TELEGRAM:
        if TELEGRAM_MODE.lower() == "bot":
            await setup_telegram_bot(logger=logger)
        elif TELEGRAM_MODE.lower() == "api":
            setup_telegram_api(logger=logger)
        else:
            logger.error("Telegram setup failed. telegram is not activated!")
    else:
        logger.warning("ACTIVE_TELEGRAM env is not set. no alerts will be sent by telegram!")
    if ACTIVE_SMS:
        SMSHandler(api_key=KAVENEGAR_API_KEY)
    else:
        logger.warning("ACTIVE_SMS env is not set. no alerts will be sent by SMS!")
    yield  
    # finishing code
    logger.info("Finishing application...")