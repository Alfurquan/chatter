from .json_logger import JsonLogger
from .standard import StandardLogger
from .base import BaseLogger

class LoggerFactory:
    """
    Factory class for creating loggers with a specific name.
    """
    @classmethod
    def create_logger(cls, name: str, logger_type: str = "standard") -> BaseLogger:
        """
        Create a logger instance based on the specified type.
        
        Args:
            name: The name of the logger
            logger_type: The type of logger to create ("standard" or "json")
        
        Returns:
            BaseLogger: An instance of the specified logger type
        """
        if logger_type == "json":
            logger_instance = JsonLogger(name)
        elif logger_type == "standard":
            logger_instance = StandardLogger(name)
        else:
            raise ValueError(f"Unknown logger type: {logger_type}")
        
        # Actually set up the logger
        logger_instance.setup()
        return logger_instance

    