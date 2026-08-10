"""Centralized Logging Module for AI Workforce Intelligence Platform."""

import logging
import sys

def get_logger(name: str = "ai_workforce") -> logging.Logger:
    """Configures and returns a standardized application logger.
    
    Args:
        name (str): The namespace for the logger instance.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = get_logger("ai_workforce.app")
