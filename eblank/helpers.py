import argparse
import sys
import logging
import glob
import os
import signal
from datetime import datetime

from eblank import settings


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='enable debug logging')
    arg_parser.add_argument('-s', '--silent', action='store_true', help='show only critical logging')
    arg_parser.add_argument('--drop', action='store_true', help='drop tables before start')
    arg_parser.add_argument('--clean', action='store_true', help='clean up data persistence')
    args = arg_parser.parse_args()

    if args.verbose and args.silent:
        raise RuntimeError('Can\'t use verbose and silent logging modes simultaneously')

    return args


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


def clean_up_shelve():
    logging.info('Cleaning up shelve...')
    for f in glob.glob(settings.SHELVE_FILENAME + '*'):
        os.remove(f)


def load_from_shelve(app, shelf):
    app_keys = ['shift', 'visitors', 'cash', 'shift', 'user_id', 'username', 'is_admin']
    any_loaded = False
    for key in app_keys:
        if key in shelf:
            any_loaded = True
            app[key] = shelf[key]
    if any_loaded:
        logging.info('Loaded system state from file.')


def save_to_shelve(app, shelf):
    app_keys = ['shift', 'visitors', 'cash', 'shift', 'user_id', 'username', 'is_admin']
    for key in app_keys:
        if key in app:
            shelf[key] = app[key]
    logging.info('Saved current system state.')


def termination_handler(signum, frame):
    raise KeyboardInterrupt("Handled signal: {}".format(signum))


def set_termination_handler():
    signal.signal(signal.SIGTERM, termination_handler)


def get_hms(seconds):
    """
    Get string in format "%H:%M:%S"
    :param seconds: float
    :return: sting
    """
    hours = str(int(seconds // 3600))
    if len(hours) == 1:
        hours = '0' + hours
    seconds %= 3600
    minutes = str(int(seconds // 60))
    if len(minutes) == 1:
        minutes = '0' + minutes
    seconds = str(int(seconds % 60))
    if len(seconds) == 1:
        seconds = '0' + seconds
    result = ':'.join((hours, minutes, seconds))
    return result


def from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S %d.%m.%Y')
