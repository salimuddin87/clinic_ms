# app/logger_config.py
import logging


def get_logger(name: str = "clinic"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        ch.setFormatter(logging.Formatter(fmt))
        logger.addHandler(ch)
    return logger
