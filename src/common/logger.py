import logging

LOG_FILE = './logs/bot.log'
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    format="%(asctime)-15s %(threadName)s %(levelname)-8s %(message)s"
)

