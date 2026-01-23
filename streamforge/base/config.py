"""
Global configuration object for StreamForge settings.

This module provides a global config object that holds
a central logger and can be extended with additional settings.
"""

from .logger import DefaultLogger, SilentLogger


class StreamForgeConfig:
    """Global configuration object for StreamForge settings."""
    
    def __init__(self):
        self._logger = DefaultLogger()
    
    @property
    def logger(self):
        """Get the current logger instance."""
        return self._logger
    
    @logger.setter
    def logger(self, value):
        """
        Set the logger instance.
        
        Accepts any object with .info(), .warning(), .error(), .debug(), .critical() methods.
        Examples: logging.getLogger(), loguru.logger, structlog.get_logger(), etc.
        """
        # Duck typing - just check if it has the required methods
        required_methods = ['info', 'warning', 'error', 'debug', 'critical']
        missing = [m for m in required_methods if not hasattr(value, m) or not callable(getattr(value, m))]
        
        if missing:
            raise TypeError(
                f"Logger must have the following callable methods: {required_methods}. "
                f"Missing: {missing}"
            )
        
        self._logger = value
    
    def set_silent(self):
        """Convenience method to set silent logger."""
        self.logger = SilentLogger()


# Global instance
config = StreamForgeConfig()

