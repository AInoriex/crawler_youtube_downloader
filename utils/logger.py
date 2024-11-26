# -*- coding: UTF8 -*-
import time
import os
import sys
from loguru import logger

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

class Logger():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        print("Logger已初始化")
        return cls._instance

    def __init__(self):
        self.logger = None

    def init_loguru(self):
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
        log_date = time.strftime("%Y-%m-%d", time.localtime())
        log_time = time.strftime("%Y%m%d.%H-%M", time.localtime())
        # 预留日志路径
        log_dir = os.path.join(os.getenv('LOG_PATH'), log_date)
        os.makedirs(log_dir, exist_ok=True)
        # 日志配置
        logger.remove(0)
        filename = os.path.join(log_dir, f"{log_time}.log")
        log_level = "DEBUG" if os.getenv('DEBUG')=='True' else "INFO"
        log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | Process.{process} | {message}"
        logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
        logger.add(
            filename,
            level=log_level,
            format=log_format,
            # 完整错误信息
            diagnose=True,
            # 错误信息回溯
            backtrace=True,
            # 启动队列处理(多进程)
            enqueue=True, 
            # 单个日志文件大小
            rotation="500MB",
            # 日志文件保留时间
            retention="15 days",
            # 日志文件压缩格式
            compression="zip",
        )
        logger.info(f"初始化日志记录器成功, 日志level:{log_level}, 日志路径:{filename}")
        self.logger = logger

g = Logger()
g.init_loguru()
logger = g.logger

if __name__ == "__main__":
    logger.debug("这是一条测试日志")
    logger.info("这是一条测试日志")
    logger.warning("这是一条测试日志")
    logger.error("这是一条测试日志")
    exit()