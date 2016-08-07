import asyncio
import logging
import argparse

from aiohttp import web
import aiohttp_jinja2
import jinja2

from setup_logging import setup_logging
from routes import routes
from models import init_db
from middlewares import authorize
from shift import open_shift
import settings


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='enable debug logging')
    arg_parser.add_argument('-s', '--silent', action='store_true', help='show only critical logging')
    arg_parser.add_argument('--drop', action='store_true', help='drop tables before start')
    args = arg_parser.parse_args()

    if args.verbose and args.silent:
        raise RuntimeError('Can\'t use verbose and silent logging modes simultaneously')

    return args


def init_app(db, loop=None):
    app = web.Application(
        middlewares=[
            authorize,
        ],
        loop=loop
    )

    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_PATH, name='static')

    app['db'] = db
    app['visitors'] = {}
    app['cash'] = 0
    app['shift'] = open_shift(cash=app['cash'])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_PATH))
    return app


def main():
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(verbose=args.verbose, silent=args.silent)
    db = init_db(args.drop)
    app = init_app(db, loop=loop)
    logging.info('Starting app on port {}...'.format(settings.PORT))
    web.run_app(app, port=settings.PORT, print=lambda x: x)
    logging.info('Stopped.')


if __name__ == '__main__':
    main()
