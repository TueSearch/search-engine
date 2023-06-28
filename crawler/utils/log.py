"""
This module contains a function for creating a logger instance.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str, max_file_size: int = 10 * 1024 * 1024, backup_count: int = 20):
    """
    Creates a logger instance with the specified name, log file name, and file size limit.

    Args:
        name (str): Logger name.
        log_file_name (str): Log file name.
        max_file_size (int): Maximum file size in bytes (default is 10 MB).
        backup_count (int): Number of backup log files to keep (default is 20).

    Returns:
        logging.Logger: Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s',
        '%d-%m %H:%M')

    log_file_name = name.split("/")[-1].split(".")[0]
    log_file_name = f'{os.getenv("LOG_FILES_PATH")}/{log_file_name}.log'
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file_name,
        maxBytes=max_file_size,
        backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    console_handler.setFormatter(formatter)

    return logger
