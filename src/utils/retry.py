from functools import wraps
import logging
import time

logger = logging.getLogger("alertbot")

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed operations with configurable parameters.

    This decorator will attempt to execute the decorated function multiple times
    if it fails with an exception. Between retries, it will wait for a specified
    delay period.

    Args:
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        delay (float, optional): Time to wait between retries in seconds. Defaults to 1.0.

    Returns:
        function: Decorated function that will retry on failure.

    Raises:
        Exception: If all retry attempts fail, the last exception is re-raised.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator