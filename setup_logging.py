import logging
import sys


def setup_logging(debug):
    fmt = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
    if debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(stream=sys.stdout, level=logging_level, format=fmt)
    logging.getLogger('tornado').setLevel(logging.WARNING)
