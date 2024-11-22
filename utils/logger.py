# -*- coding: UTF8 -*-
import time
import os

def init_logger(name):
    """
    Initializes a logger with logging package.

    The logger is configured to have different log levels based on the DEBUG environment variable.
    If DEBUG is set to 'True', the log level is set to DEBUG; otherwise, it is set to INFO.
    The logger outputs logs to both a file and the console. The log files are stored in a directory
    specified by the LOG_PATH environment variable, organized by date.

    The console output includes color formatting for different log levels:
    - ERROR messages are displayed in red.
    - WARNING messages are displayed in yellow.
    - INFO messages are displayed in blue.
    - DEBUG messages are displayed in green.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger.
    """
    import logging
    logger = logging.getLogger(name)
    if os.getenv('DEBUG') == 'True':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Add file handler to save logs to a file
    log_date = time.strftime("%Y-%m-%d", time.localtime())
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())

    log_dir = os.path.join(os.getenv('LOG_PATH'), log_date)
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh = logging.FileHandler(os.path.join(log_dir, f"{log_time}.log"))
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # 创建一个自定义的日志格式器，将特定级别的日志设置为红色
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            if record.levelno >= logging.ERROR:
                record.msg = "\033[1;31m" + str(record.msg) + "\033[0m"
            elif record.levelno >= logging.WARNING:
                record.msg = "\033[1;33m" + str(record.msg) + "\033[0m"
            elif record.levelno >= logging.INFO:
                record.msg = "\033[1;34m" + str(record.msg) + "\033[0m"
            elif record.levelno >= logging.DEBUG:
                record.msg = "\033[1;32m" + str(record.msg) + "\033[0m"
            return super().format(record)
        

    color_formatter = ColorFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch = logging.StreamHandler()
    ch.setFormatter(color_formatter)
    logger.addHandler(ch)

    return logger

def init_loguru():
    """
    Initializes a logger with loguru package.

    The logger is configured to have different log levels based on the DEBUG environment variable.
    If DEBUG is set to 'True', the log level is set to DEBUG; otherwise, it is set to INFO.
    The logger outputs logs to both a file and the console. The log files are stored in a directory
    specified by the LOG_PATH environment variable, organized by date.

    Args:
        None

    Returns:
        logging.Logger: The configured logger.
    """
    from loguru import logger
    log_date = time.strftime("%Y-%m-%d", time.localtime())
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())

    log_dir = os.path.join(os.getenv('LOG_PATH'), log_date)
    os.makedirs(log_dir, exist_ok=True)

    filename = os.path.join(log_dir, f"{log_time}.log")
    logger.add(
        filename,
        level= "DEBUG" if os.getenv('DEBUG')=='True' else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {file:line} | {level} | {message}",
    )
    return logger
logger = init_loguru()
