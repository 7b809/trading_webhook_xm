import logging
from config import Config

logger = logging.getLogger("webhook_logger")

if Config.TEST_LOG:
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger.addHandler(console)
else:
    logger.disabled = True