class LotoesCommandError(Exception):
    """Raise when the KEY-VALUE store encounters a runtime error."""
    def __init__(self, message):
        self.message = message
