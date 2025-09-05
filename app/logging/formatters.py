import logging
import json
from .config import LOGGING_CONFIG

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
        self.reserved_attrs = set(logging.LogRecord(None, None, "", 0, "", (), None).__dict__.keys())
    
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "logger": record.name,
        }
        for key, value in record.__dict__.items():
            if key not in self.reserved_attrs:
                log_record[key] = value
       
        return json.dumps(log_record)