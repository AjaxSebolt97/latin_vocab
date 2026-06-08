"""
Logging configuration for Latin Vocab tool.

Sets up logging for all modules with appropriate handlers and formatting.
"""

import logging
import logging.handlers
from pathlib import Path

import config

# Root logger
logger = logging.getLogger()


def setup_logging(level: str = "INFO", log_file: Path = None):
    """
    Configure logging for the application.
    
    Sets up both console and file handlers with consistent formatting.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional path to log file (default: config.get_log_file())
    """
    if log_file is None:
        log_file = config.get_log_file()
    
    # Set root logger level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (all levels)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging configured at level {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on module load
setup_logging(level=config.LOG_LEVEL)
