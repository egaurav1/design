# src/logger.py
"""Logging configuration for video analyzer"""

import logging
import sys
from pathlib import Path
from .config import settings

def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with console and file handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    log_file = settings.LOGS_DIR / f"{name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create root logger
logger = setup_logger("video_analyzer")

if __name__ == "__main__":
    # Test the logger
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
