import logging


class SpecialFilter(logging.Filter):
    """
    Custom filter for logging configuration.
    """

    def __init__(self, foo=None):
        super().__init__()
        self.foo = foo

    def filter(self, record):
        # Add custom filtering logic here if needed
        return True
