import logging
import shelve

import aiohttp_jinja2
import asyncio
import jinja2
from aiohttp import web

from eblank import settings
from eblank.middlewares import authorize
from eblank.models import init_db
from eblank.routes import routes
from eblank.shift import open_shift
from eblank.helpers import parse_args, setup_logging, save_to_shelve, load_from_shelve, clean_up_shelve


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


def init_shelve(clean=False):
    if clean:
        clean_up_shelve()
    shelf = shelve.open(settings.SHELVE_FILENAME)
    return shelf


def main():
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(verbose=args.verbose, silent=args.silent)
    db = init_db(args.drop)
    app = init_app(db, loop=loop)
    shelf = init_shelve(args.clean)
    load_from_shelve(app, shelf)
    logging.info('Starting app on port {}...'.format(settings.PORT))
    try:
        web.run_app(app, port=settings.PORT, print=lambda x: x)
    finally:
        save_to_shelve(app, shelf)
        logging.info('Stopped.')


if __name__ == '__main__':
    main()
