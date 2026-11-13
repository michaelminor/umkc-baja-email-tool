"""
Logging configuration for the email automation tool.
Provides both file and console logging with different verbosity levels.
"""

import logging
import os
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows color support
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output."""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(log_dir="logs", verbose=False):
    """
    Create and configure logger with both file and console handlers.

    Args:
        log_dir: Directory to store log files
        verbose: If True, console shows DEBUG level; if False, shows INFO level

    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"email_automation_{timestamp}.log")

    # Configure logger
    logger = logging.getLogger("EmailAutomation")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # Console handler - important messages only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_format = ColoredFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger
