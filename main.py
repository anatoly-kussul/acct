import asyncio
import logging
import argparse

from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_jinja2
import jinja2

from setup_logging import setup_logging
from routes import routes
import settings


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--debug', action='store_true', help='enable debug logging')
    args = arg_parser.parse_args()
    return args


def main():
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(args.debug)
    app = web.Application(
        middlewares=[
            session_middleware(EncryptedCookieStorage(settings.SECRET_KEY)),
        ],
        loop=loop
    )
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_PATH, name='static')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_PATH))

    logging.info('Starting app on port {}...'.format(settings.PORT))
    try:
        web.run_app(app, port=settings.PORT)
    except KeyboardInterrupt:
        logging.info('Shutting down due to KeyboardInterrupt...')
    logging.info('Stopped.')


if __name__ == '__main__':
    main()
