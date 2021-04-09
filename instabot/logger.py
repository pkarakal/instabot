import logging
import logging.handlers
import logging.config

default_logger = logging.getLogger("instabot")
logging_file = "instabot.log"
logging.basicConfig(filename=logging_file, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
default_logger.setLevel(logging.DEBUG)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
    logging_file, backupCount=5)

default_logger.addHandler(handler)


def stopLogging():
    logging.config.stopListening()
