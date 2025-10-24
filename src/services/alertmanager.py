import logging
from typing import Dict, List, Optional, Union
from utils import make_api_call
# Configure logger
logger = logging.getLogger("alertbot")

class AlertManagerClient:
    """AlertManager API client that provides direct methods for each endpoint."""
    
    API_VERSION = "v2"
    
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize AlertManager API client.

        Args:
            base_url (str): Base URL of the AlertManager instance
            username (str, optional): Username for basic auth
            password (str, optional): Password for basic auth
        """
        self.base_url = f"{base_url.rstrip('/')}/api/{self.API_VERSION}"
        self.auth = (username, password) if username and password else None
        logger.info(f"Initialized AlertManagerClient with base URL: {self.base_url}")

    def get_alerts(self, filter_params: Optional[Dict] = None) -> List[Dict]:
        """Get all alerts from AlertManager.

        Args:
            filter_params (dict, optional): Filter parameters for alerts

        Returns:
            List[dict]: List of alerts
        """
        url = f"{self.base_url}/alerts"
        logger.info(f"Getting alerts with filters: {filter_params}")
        logger.debug(f"Making GET request to {url}")
        
        response = make_api_call(
            method="GET",
            url=url,
            headers={"Accept": "application/json"},
            params=filter_params,
            retry_count=3
        )
        response.raise_for_status()
        alerts = response.json()
        logger.info(f"Retrieved {len(alerts)} alerts")
        return alerts


    def post_alerts(self, alerts: Union[Dict, List[Dict]]) -> None:
        """Post new alerts to AlertManager.

        Args:
            alerts (Union[Dict, List[Dict]]): Alert or list of alerts to post
        """
        url = f"{self.base_url}/alerts"
        if isinstance(alerts, dict):
            alerts = [alerts]

        logger.info(f"Posting {len(alerts)} alerts")
        logger.debug(f"Making POST request to {url}")

        response = make_api_call(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            payload=alerts,
            retry_count=3
        )
        return response.raise_for_status()


    def get_silences(self) -> List[Dict]:
        """Get all silences from AlertManager.

        Returns:
            List[Dict]: List of silences
        """
        url = f"{self.base_url}/silences"
        logger.info("Getting all silences")
        logger.debug(f"Making GET request to {url}")

        response = make_api_call(
            method="GET",
            url=url,
            headers={"Accept": "application/json"},
            retry_count=3
        )
        response.raise_for_status()
        silences = response.json()
        logger.info(f"Retrieved {len(silences)} silences")
        return silences

    def create_silence(self, silence_data: Dict) -> str:
        """Create a new silence.

        Args:
            silence_data (Dict): Silence configuration

        Returns:
            str: Silence ID
        """
        url = f"{self.base_url}/silences"
        logger.info("Creating silence")
        logger.debug(f"Making POST request to {url}")

        response = make_api_call(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            payload=silence_data,
            retry_count=3
        )
        response.raise_for_status()
        silence_id = response.json()['silenceID']
        logger.info(f"Created silence with ID: {silence_id}")
        return silence_id

    def delete_silence(self, silence_id: str) -> None:
        """Delete a silence by ID.

        Args:
            silence_id (str): ID of the silence to delete
        """
        url = f"{self.base_url}/silence/{silence_id}"
        logger.info(f"Deleting silence with ID: {silence_id}")
        logger.debug(f"Making DELETE request to {url}")

        response = make_api_call(
            method="DELETE",
            url=url,
            headers={"Accept": "application/json"},
            retry_count=3
        )
        response.raise_for_status()
        logger.info(f"Successfully deleted silence: {silence_id}")
