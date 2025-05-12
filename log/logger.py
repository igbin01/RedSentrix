# log/logger.py
import logging

def setup_logger():
    logger = logging.getLogger('Nebula Drift')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = setup_logger()

def log_event(event):
    logger.info(event)
