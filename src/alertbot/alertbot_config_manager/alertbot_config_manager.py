from alertbot.env import CONFIG_JSON_FILE, CONFIG_SPLUNK_JSON_FILE
from alertbot.constants import CONFIG_DESTINATIONS_KEYWORD, \
    TELEGRAM_CONFIG_WORD
from .exceptions import BadJsonConfigFile, \
    KeyWordNotFound
import json
import logging

class ConfigManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alertbot_config = None
        self.alertbot_splunk_config = {}
    
    def read_alertbot_configs(self):
        with open(CONFIG_JSON_FILE, 'r') as file:
            try:
                self.alertbot_config = json.load(file)
                self.logger.info(f"Successfully parsed {CONFIG_JSON_FILE}")
            except json.JSONDecodeError as json_err:
                self.logger.error(f"Error decoding {CONFIG_JSON_FILE}, error: {json_err}")
                raise BadJsonConfigFile(f"Error at reading json config file {json_err}")  
            else:
                self.validate_alertbot_configs() # we validate the main configs that are for prometheus
                
    def read_alertbot_splunk_configs(self):
        with open(CONFIG_SPLUNK_JSON_FILE, 'r') as file:
            try:
                self.alertbot_splunk_config = json.load(file)
                self.logger.info(f"Successfully parsed {CONFIG_SPLUNK_JSON_FILE}")
            except json.JSONDecodeError as json_err:
                self.logger.error(f"Error decoding {CONFIG_SPLUNK_JSON_FILE}, error: {json_err}")
                self.logger.error(f"No splunk config were added.") # No validation for splunk configs

    def validate_alertbot_configs(self):
        destinations = self.alertbot_config.get(CONFIG_DESTINATIONS_KEYWORD, None)
        if destinations == None:
            raise KeyWordNotFound(f"{CONFIG_DESTINATIONS_KEYWORD} not found in json config!")
        for index,dest in enumerate(destinations):
            if dest.get("receiver", None) == None:
                raise KeyWordNotFound(f"receiver not found in destinations_{index} in json config!")
            if dest.get("severity", None) == None:
                raise KeyWordNotFound(f"severity not found in destinations_{index} in json config!")
            
            self.validate_alertbot_type(dest.get("types", None), index)
    
    def validate_alertbot_type(self, types: list, index: int):
        if types == None:
            raise KeyWordNotFound(f"types not found in destinations_{index} in json config!")
        for index_type, type in enumerate(types):
            if type.get("type", None) == None:
                raise KeyWordNotFound(f"type not found in destinations_{index}, types_{index_type} in json config!")
            if type.get("type") == TELEGRAM_CONFIG_WORD:
                self.validate_telegram_type(type)
    
    def validate_telegram_type(self, type: dict):
        if type.get("telegram_group_id") == None:
            raise KeyWordNotFound(f"telegram_group_id not found for type telegram in alertbot config!")

    def get_alertbot_config(self):
        return self.alertbot_config

    def get_alertbot_splunk_config(self):
        return self.alertbot_splunk_config