"""
Default logger implementations for StreamForge.

This module provides default logger wrappers around Python's logging module
and a silent logger for no-op logging.
"""

import logging


class DefaultLogger:
    """
    Default logger wrapper around Python's logging module.
    
    Supports three modes:
    - Console only: log_file=None, console=True
    - File only: log_file="path.log", console=False
    - Both: log_file="path.log", console=True
    """
    
    def __init__(self, log_file=None, console=True, name="streamforge"):
        """
        Initialize default logger.
        
        Args:
            log_file: Optional file path to write logs to. If None, no file logging.
            console: If True, log to console/terminal. If False, no console output.
            name: Logger name (default: "streamforge")
        """
        self._logger = logging.getLogger(name)
        self._log_file = log_file
        self._console = console
        
        # Create formatter with timestamps
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Clear existing handlers to ensure clean setup
        self._logger.handlers.clear()
        
        # Add console handler if enabled
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        # Add file handler if log_file is provided
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        
        self._logger.setLevel(logging.INFO)
    
    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)


class SilentLogger:
    """No-op logger for silent mode."""
    
    def info(self, msg, *args, **kwargs):
        pass
    
    def warning(self, msg, *args, **kwargs):
        pass
    
    def error(self, msg, *args, **kwargs):
        pass
    
    def debug(self, msg, *args, **kwargs):
        pass
    
    def critical(self, msg, *args, **kwargs):
        pass

