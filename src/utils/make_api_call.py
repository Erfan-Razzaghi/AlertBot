from .metrics import api_call_status_count
import requests
import time
import logging

logger = logging.getLogger("alertbot")

def make_api_call(
        method: str, # GET, POST, etc.
        url: str, 
        headers: dict = {},
        payload: dict = None,
        params: dict = {},
        retry_count: int = 1,
        verify: bool = True,
        retry_interval: float = 0.5):
    response = None
    for i in range(retry_count):
        try:
            logger.debug(f"Calling {url} with method {method}")
            response = requests.request(method, url, headers=headers, data=payload, params=params,
                                        verify=verify)
        except Exception as e:
            logger.error(f"Error Happened During calling {url} with method {method}")
            logger.error(f"{e}")
            time.sleep(retry_interval)
        else:
            api_call_status_count.labels(
                    destination=url, 
                    status_code=response.status_code, 
                    method=method
            ).inc()
            if response.status_code < 400:
                logger.debug(f"{url} Called Successfuly, Response Status Code: {response.status_code}")
                break
            logger.error(f"Got Status error code{response.status_code} during calling {url}")


    
    return response
