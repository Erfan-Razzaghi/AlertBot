class TemplateTelegramError(Exception):
    def __init__(self):
        message = "Error happened during creating the template for telegram message"
        super().__init__(f"{message}")