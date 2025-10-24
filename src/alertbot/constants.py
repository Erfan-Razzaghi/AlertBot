LOG_COLORS={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
}
LOG_FORMAT = "[%(asctime)s] [%(log_color)s%(levelname)-s%(reset)s] [%(cyan)s%(module)s%(reset)s] %(message)s"
DATE_FORMAT = "%H:%M:%S %z"

CONFIGS_DIRECTORY = "configs/"
CONFIG_DESTINATIONS_KEYWORD = "destinations"
TELEGRAM_CONFIG_WORD = "telegram"
TELEGRAM_MAX_MESSAGE_LENGTH = 4000
SMS_CONFIG_WORD = "sms" 
SMS_LIMIT_ERROR_MESSAGE = "There are ##NUMBER## more messages related to alertname ##ALERTNAME## skipped for your convenience."