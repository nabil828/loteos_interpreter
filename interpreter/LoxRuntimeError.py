class LoxRuntimeError(Exception):
    """Raise when the Loteos interpreter encounters a runtime error."""
    def __init__(self, token, message):
        self.token = token
        self.message = message
