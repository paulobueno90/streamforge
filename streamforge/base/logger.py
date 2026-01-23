"""
Default logger implementations for StreamForge.

This module provides default logger wrappers around Python's logging module
and a silent logger for no-op logging.
"""

import logging


class DefaultLogger:
    """Default logger wrapper around Python's logging module."""
    
    def __init__(self, name="streamforge", silent=False):
        self._logger = logging.getLogger(name)
        self._silent = silent
        
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
    
    def info(self, msg, *args, **kwargs):
        if not self._silent:
            self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        if not self._silent:
            self._logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        if not self._silent:
            self._logger.error(msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        if not self._silent:
            self._logger.debug(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        if not self._silent:
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

