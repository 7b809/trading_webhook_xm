import logging
from config.settings import TEST_LOG
def get_logger(name):
    logger=logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.DEBUG if TEST_LOG else logging.INFO)
    h=logging.StreamHandler();
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(h); return logger
