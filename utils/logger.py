"""
Logger configuration.
"""
import logging
import logging.handlers
import os
from pathlib import Path
from config.settings import settings

# Create logs directory if it doesn't exist
log_dir = Path(settings.log_file).parent
log_dir.mkdir(parents=True, exist_ok=True)

# Create logger
logger = logging.getLogger("chatbot")
logger.setLevel(getattr(logging, settings.log_level))

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    settings.log_file,
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setLevel(getattr(logging, settings.log_level))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"chatbot.{name}")
