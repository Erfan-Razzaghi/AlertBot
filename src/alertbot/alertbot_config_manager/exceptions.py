import logging
class CustomError(Exception):
    pass
class BadJsonConfigFile(CustomError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class KeyWordNotFound(CustomError):
    def __init__(self, message):
        logger = logging.getLogger(__name__)
        logger.error(message)
        self.message = message
        super().__init__(self.message)
