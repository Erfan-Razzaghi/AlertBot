
class SMSSplunkTemplater:
    def __init__(self, keys: list, request_body: dict):
        self.keys = keys
        self.request_body = request_body
        self.message = ""
        self.generate_message()

    def generate_message(self):
        # Implement the logic to generate the SMS message
        for key in self.keys:
            self.message += f"{key}: "
            self.message += str(self.request_body.get(key, "No value!"))
            self.message += "\n"

    def get_message(self):
        return self.message
    