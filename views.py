from hashlib import md5
import json
import time
import uuid
from operator import itemgetter

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session
from peewee import IntegrityError

from models import User, Visitor
import settings


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
    async def get(self):
        session = await get_session(self.request)
        return {
            'data': 'Hello Kitty ^_^',
            'username': session.get('username'),
            'is_admin': session.get('is_admin'),
            'visitors': sorted(self.request.app['visitors'].values(), key=itemgetter('time_in')),
        }


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


class AddVisitorView(web.View):
    @aiohttp_jinja2.template('add_visitor.html')
    async def get(self):
        return {}

    async def post(self):
        data = await self.request.post()
        _id = str(uuid.uuid4())
        visitor = {
            'id': _id,
            'name': data['name'],
            'time_in': time.time(),
        }
        self.request.app['visitors'][_id] = visitor
        redirect(self.request, 'main')


class RemoveVisitorView(web.View):
    @aiohttp_jinja2.template('remove_visitor.html')
    async def get(self):
        data = self.request.GET
        visitor_id = data['id']
        visitor = self.request.app['visitors'].get(visitor_id)
        if visitor is None:
            redirect(self.request, 'main')
        visitor['time_out'] = time.time()
        visitor['time_delta'] = visitor['time_out'] - visitor['time_in']
        visitor['price'] = int(visitor['time_delta']/3600 * settings.HOUR_PRICE * 2)/2
        return visitor

    async def post(self):
        data = await self.request.post()
        visitor_id = data['id']
        visitor = self.request.app['visitors'].pop(visitor_id, None)
        if visitor is None:
            return web.Response(
                content_type='application/json',
                text=json.dumps({'error': 'There is no visitor with such id'})
            )
        visitor.pop('id')
        visitor['paid'] = float(data['paid'])
        Visitor.create(**visitor)
        redirect(self.request, 'main')
