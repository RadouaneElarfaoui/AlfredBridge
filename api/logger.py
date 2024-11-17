import logging

def setup_logger(name):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger 