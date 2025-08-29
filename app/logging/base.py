"""
Base logger interface for the factory pattern.

This module defines the abstract base class that all logger implementations
must follow, ensuring a consistent interface across different logger types.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any


class BaseLogger(ABC):
    """
    Abstract base class for all logger implementations.
    
    This ensures all logger types (JSON, Standard, etc.) have a consistent interface
    and can be used interchangeably through the factory pattern.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base logger.
        
        Args:
            name: The name of the logger
        """
        self.name = name
        self._logger: logging.Logger = None
    
    @abstractmethod
    def setup(self) -> logging.Logger:
        """
        Set up and configure the logger.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        pass
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            logging.Logger: The logger instance
        """
        if self._logger is None:
            self._logger = self.setup()
        return self._logger
    
    # Convenience methods that delegate to the underlying logger
    def debug(self, msg: Any, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: Any, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: Any, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: Any, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: Any, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)
