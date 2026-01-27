"""
Global configuration object for StreamForge settings.

This module provides a global config object that holds
a central logger and can be extended with additional settings.
"""

from .logger import DefaultLogger, SilentLogger


class StreamForgeConfig:
    """Global configuration object for StreamForge settings."""
    
    def __init__(self):
        # Default: SilentLogger (no logging)
        self._logger = SilentLogger()
    
    @property
    def logger(self):
        """Get the current logger instance."""
        return self._logger
    
    @logger.setter
    def logger(self, value):
        """
        Set a custom logger instance.
        
        Accepts any object with .info(), .warning(), .error(), .debug(), .critical() methods.
        Examples: logging.getLogger(), loguru.logger, structlog.get_logger(), etc.
        
        Note: Custom loggers are expected to have their own configuration.
        This method is for users who want to use their own logging setup.
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
    
    def set_log_file(self, log_file: str, console: bool = False):
        """
        Activate the default logger and configure file logging.
        
        This creates a DefaultLogger instance with file logging enabled.
        By default, logs go to file only (no console output).
        
        Args:
            log_file: Path to the log file where logs will be written.
            console: If True, also log to console/terminal. If False, file only (default: False).
        
        Examples:
            >>> # File only (no console output)
            >>> sf.config.set_log_file("app.log")
            
            >>> # File and console
            >>> sf.config.set_log_file("app.log", console=True)
        """
        self._logger = DefaultLogger(log_file=log_file, console=console)
    
    def set_console_only(self):
        """
        Activate the default logger with console output only (no file).
        
        Examples:
            >>> sf.config.set_console_only()
            >>> # Now logs appear in terminal only
        """
        self._logger = DefaultLogger(log_file=None, console=True)
    
    def set_silent(self):
        """Disable all logging (default state)."""
        self._logger = SilentLogger()


# Global instance
config = StreamForgeConfig()

