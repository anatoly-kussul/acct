from aiohttp import web
import aiohttp_jinja2


class MainView(web.View):
    @aiohttp_jinja2.template('index.html')
    def get(self):
        return {'data': 'Hello Kitty ^_^'}
