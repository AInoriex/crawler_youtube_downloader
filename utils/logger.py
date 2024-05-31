import logging
import time
import os
from utils.tool import load_cfg

def init_logger(name):
    cfg = load_cfg("config.json")

    logger = logging.getLogger(name)
    if cfg["common"]["debug_mode"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Add file handler to save logs to a file
    log_date = time.strftime("%Y-%m-%d", time.localtime())
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())

    log_dir = os.path.join(cfg["common"]["log_path"], log_date) 
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
