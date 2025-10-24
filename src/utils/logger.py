import logging
import sys
import time
from alertbot.env import LOG_LEVEL
from alertbot.constants import LOG_FORMAT, DATE_FORMAT, LOG_COLORS
from colorlog import ColoredFormatter

class LocalTimeFormatter(ColoredFormatter):
    """Custom formatter that uses local time instead of UTC"""
    
    def formatTime(self, record, datefmt=None):
        """Override formatTime to use local time"""
        # Convert the record time to local time
        local_time = time.localtime(record.created)
        if datefmt:
            return time.strftime(datefmt, local_time)
        else:
            return time.strftime(DATE_FORMAT, local_time)

def setup_logging(log_level=None):
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger: Configured logger instance
    """
    # Get log level from environment or use default
    if log_level is None:
        log_level_name = LOG_LEVEL
        log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Clear any existing handlers from the root logger
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    
    # Create console handler with a specific formatter
    formatter = LocalTimeFormatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
        reset=True,
        log_colors=LOG_COLORS
    )
    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)
    
    # Configure the root logger with just the console handler
    root.setLevel(log_level)
    root.addHandler(console_handler)
    
    # Get our application logger
    logger = logging.getLogger("alertbot")
    logger.setLevel(log_level)
    
    # Add a startup message to verify logging is working
    logger.info(f"Alertbot logger initialized (Level: {log_level_name})")

    # Silence noisy third-party loggers
    # logging.getLogger("telegram").setLevel(logging.WARNING) #this is an example, uncomment if needed

    return logger