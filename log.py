import logging

logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
# log to file
# logging.basicConfig(filename='../log/output.log', encoding='utf-8', level=logging.INFO)

def log_info(msg):
    logging.info(msg)
    return 

def log_debug(msg):
    logging.debug(msg)
    return 

def log_error(msg):
    logging.error(msg)
    return

