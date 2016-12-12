from aiohttp import web

async def authorize(app, handler):
    async def middleware(request):
        def check_path(path):
            result = True
            for r in ['/login', '/static/']:
                if path.startswith(r):
                    result = False
            return result

        if app.get("username"):
            return await handler(request)
        elif check_path(request.path):
            url = request.app.router['login'].url()
            raise web.HTTPFound(url)
        else:
            return await handler(request)

    return middleware
