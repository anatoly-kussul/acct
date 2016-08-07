import logging
import sys


def setup_logging(verbose=False, silent=False):
    fmt = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
    if verbose:
        logging_level = logging.DEBUG
    elif silent:
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.INFO
    logging.basicConfig(stream=sys.stdout, level=logging_level, format=fmt)
    if not verbose:
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
