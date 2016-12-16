import logging
import shelve
import psutil
import os
import time

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


def init_app(loop=None):
    app = web.Application(
        middlewares=[
            authorize,
        ],
        loop=loop
    )

    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_PATH, name='static')

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
        chrome_app = run_chrome_app()
        asyncio.ensure_future(wait_for_process(chrome_app, loop=loop), loop=loop)
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


async def wait_for_process(process, loop=None):
    while process.is_running():
        await asyncio.sleep(0.1, loop=loop)
    logging.info('Eblank process stopped')
    loop.stop()


def get_chrome_processess():
    chrome_pids = set()
    for proc in psutil.process_iter():
        try:
            if proc.name() == "chrome.exe":
                chrome_pids.add(proc.pid)
        except psutil.AccessDenied:
            logging.warning("Permission error or access denied on process")

    return chrome_pids


def run_chrome_app():
    chromes_before = get_chrome_processess()
    os.system('start chrome --app=\"http://localhost:8853\"')
    eblank_process = None
    total_sleep_time = 0
    logging.info('Trying to find chrome process')
    while not eblank_process:
        time.sleep(0.1)
        total_sleep_time += .1
        chromes_after = get_chrome_processess()
        unique_pids = chromes_after - chromes_before
        if not unique_pids:
            continue
        if len(unique_pids) > 1:
            logging.critical('Found more than one started chrome processes')
            return
        eblank_pid = next(iter(unique_pids))
        try:
            eblank_process = psutil.Process(eblank_pid)
        except psutil.NoSuchProcess:
            logging.warning('no such process')
    logging.info('Found Eblank process in {} seconds (PID: {})'.format(total_sleep_time, eblank_pid))
    return eblank_process


def main():
    set_termination_handler()
    loop = asyncio.get_event_loop()
    args = parse_args()
    setup_logging(verbose=args.verbose, silent=args.silent)
    init_db(args.drop)
    app = init_app(loop=loop)
    shelf = init_shelve(args.clean)
    load_from_shelve(app, shelf)
    logging.info('Starting app on port {}...'.format(settings.PORT))
    try:
        run_app(app, port=settings.PORT, host='127.0.0.1')
    finally:
        save_to_shelve(app, shelf)
        logging.info('Stopped.')


if __name__ == '__main__':
    main()
