import logging

from .base import BaseLogger
from .formatters import JsonFormatter
from .config import LOGGING_CONFIG

class JsonLogger(BaseLogger):
    """
    JSON logger implementation that formats logs as JSON objects.
    This logger can be configured to log messages in a JSON format.
    """
    def __init__(self, name: str):
        super().__init__(name)
    
    def setup(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        
        # Check if logger already has handlers to avoid duplication
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            logger.addHandler(handler)
            logger.setLevel(LOGGING_CONFIG.get("DEFAULT_LOG_LEVEL", "INFO"))
        
        return logger