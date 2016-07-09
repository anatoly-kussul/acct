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
from models import create_tables, drop_tables
from middlewares import authorize
import settings


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--debug', action='store_true', help='enable debug logging')
    arg_parser.add_argument('--drop', action='store_true', help='drop tables before start')
    args = arg_parser.parse_args()
    return args


def init_app(loop=None):
    app = web.Application(
        middlewares=[
            session_middleware(EncryptedCookieStorage(settings.SECRET_KEY)),
            authorize,
        ],
        loop=loop
    )

    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_PATH, name='static')

    app['visitors'] = []

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_PATH))
    return app


def main():
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(args.debug)
    create_tables()
    if args.drop:
        drop_tables()
    app = init_app(loop=loop)
    logging.info('Starting app on port {}...'.format(settings.PORT))
    web.run_app(app, port=settings.PORT)
    logging.info('Stopped.')


if __name__ == '__main__':
    main()
