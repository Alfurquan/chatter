import logging
from app.config.configuration import LOGGING_CONFIG
import json

class StandardFormatter(logging.Formatter):
    """
    Standard log formatter that uses a simple text format.
    """
    def __init__(self, fmt=None, datefmt=None):
        default_fmt = LOGGING_CONFIG.get("DEFAULT_LOG_FORMAT", "[%(asctime)s] %(levelname)s - %(name)s - %(message)s")
        super().__init__(fmt=fmt or default_fmt, datefmt=datefmt)
        
class JsonFormatter(logging.Formatter):
    """
    JSON log formatter that formats logs as JSON objects.
    """
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
    
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "logger": record.name,
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)