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
from eblank.helpers import (
    parse_args,
    setup_logging,
    save_to_shelve,
    load_from_shelve,
    clean_up_shelve,
    set_termination_handler,
    from_timestamp,
    get_hms,
)


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
    app[aiohttp_jinja2.APP_KEY].filters['fromtimestamp'] = from_timestamp
    app[aiohttp_jinja2.APP_KEY].filters['get_hms'] = get_hms
    return app


def init_shelve(clean=False):
    if clean:
        clean_up_shelve()
    shelf = shelve.open(settings.SHELVE_FILENAME)
    return shelf


def run_app(app, *, host='0.0.0.0', port=None,
            shutdown_timeout=60.0, ssl_context=None):
    """Run an app locally"""
    if port is None:
        if not ssl_context:
            port = 8080
        else:
            port = 8443

    loop = app.loop

    handler = app.make_handler()
    srv = loop.run_until_complete(loop.create_server(handler, host, port,
                                                     ssl=ssl_context))

    scheme = 'https' if ssl_context else 'http'
    prompt = '127.0.0.1' if host == '0.0.0.0' else host
    logging.info("Started on {scheme}://{prompt}:{port}/".format(scheme=scheme, prompt=prompt, port=port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no branch
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.finish_connections(shutdown_timeout))
        loop.run_until_complete(app.cleanup())
    loop.close()


def main():
    set_termination_handler()
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(verbose=args.verbose, silent=args.silent)
    db = init_db(args.drop)
    app = init_app(db, loop=loop)
    shelf = init_shelve(args.clean)
    load_from_shelve(app, shelf)
    logging.info('Starting app on port {}...'.format(settings.PORT))
    try:
        run_app(app, port=settings.PORT)
    finally:
        save_to_shelve(app, shelf)
        logging.info('Stopped.')


if __name__ == '__main__':
    main()
