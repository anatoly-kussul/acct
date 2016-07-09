from hashlib import md5
import json

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session
from peewee import IntegrityError

from models import User


def redirect(request, router_name):
    url = request.app.router[router_name].url()
    raise web.HTTPFound(url)


def set_session(session, user, request):
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    redirect(request, 'main')


def end_session(session, request):
    del session['username']
    del session['is_admin']
    redirect(request, 'login')


def hash_password(password):
    return md5(password.encode('utf-8')).hexdigest()


class MainView(web.View):
    @aiohttp_jinja2.template('index.html')
    def get(self):
        return {'data': 'Hello Kitty ^_^'}


class LoginView(web.View):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('username'):
            redirect(self.request, 'main')
        return {'data': 'Please enter your login'}

    async def post(self):
        data = await self.request.post()
        try:
            user = User.get(
                username=data['username'],
                password=hash_password(data['password']),
            )
        except User.DoesNotExist:
            return web.Response(
                content_type='application/json',
                text=json.dumps({'error': 'Wrong username or password'})
            )
        else:
            session = await get_session(self.request)
            set_session(session, user, self.request)


class SignInView(web.View):
    @aiohttp_jinja2.template('sign.html')
    async def get(self):
        session = await get_session(self.request)
        if not session.get('is_admin'):
            redirect(self.request, 'main')
        return {'data': 'Please enter your data'}

    async def post(self):
        data = await self.request.post()
        try:
            user_data = {
                'username': data['username'],
                'password': hash_password(data['password']),
                'is_admin': data.get('is_admin', False)
            }
            User.create(**user_data)
        except IntegrityError:
            return web.Response(
                content_type='application/json',
                text=json.dumps({'data': 'Username is already taken'})
            )
        return web.Response(
            content_type='application/json',
            text=json.dumps({'data': 'User successfully registered'})
        )


class LogOutView(web.View):
    async def get(self):
        session = await get_session(self.request)
        end_session(session, self.request)
