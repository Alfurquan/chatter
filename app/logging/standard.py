import logging

from .base import BaseLogger
from .formatters import StandardFormatter
from .config import LOGGING_CONFIG

class StandardLogger(BaseLogger):
    """
    Standard logger implementation that uses Python's built-in logging module.
    This logger can be configured to log messages in a standard format.
    """
    def __init__(self, name: str):
        super().__init__(name)
    
    def setup(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        
        # Check if logger already has handlers to avoid duplication
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(StandardFormatter())
            logger.addHandler(handler)
            logger.setLevel(LOGGING_CONFIG.get("DEFAULT_LOG_LEVEL", "INFO"))
        
        return logger