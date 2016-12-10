import json
import time
import uuid
from hashlib import md5
from operator import itemgetter

import aiohttp_jinja2
from aiohttp import web
from peewee import IntegrityError

from eblank import settings
from eblank.db_getters import get_shifts
from eblank.models import User
from eblank.shift import close_shift, open_shift


def redirect(request, router_name):
    url = request.app.router[router_name].url()
    raise web.HTTPFound(url)


def hash_password(password):
    return md5(password.encode('utf-8')).hexdigest()


def logout(request):
    del request.app['user_id']
    del request.app['username']
    del request.app['is_admin']
    redirect(request, 'login')


class BaseView(web.View):
    @property
    def app(self):
        return self.request.app

    @property
    def db(self):
        return self.request.app.get('db')


class MainView(BaseView):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {
            'data': 'Hello Kitty ^_^',
            'username': self.app['username'],
            'is_admin': self.app['is_admin'],
            'shift': self.app['shift'],
            'visitors': sorted(self.app['visitors'].values(), key=itemgetter('time_in_timestamp')),
            'timestamp': time.time(),
        }


class LoginView(BaseView):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        if self.app.get('username'):
            redirect(self.request, 'main')
        return {}

    @aiohttp_jinja2.template('login.html')
    async def post(self):
        data = await self.request.post()
        try:
            user = await self.db.get(
                User,
                username=data['username'],
                password=hash_password(data['password']),
            )
        except User.DoesNotExist:
            return {'error': 'Wrong username or password'}
        self.app['user_id'] = user.id
        self.app['username'] = user.username
        self.app['is_admin'] = user.is_admin
        self.app['shift'] = open_shift(cash=self.app['cash'])
        redirect(self.request, 'main')


class RegisterView(BaseView):
    async def post(self):
        if not self.app.get('is_admin'):
            redirect(self.request, 'main')
        data = await self.request.post()
        try:
            user_data = {
                'username': data['username'],
                'password': hash_password(data['password']),
                'is_admin': data.get('is_admin', False)
            }
            await self.db.create(User, **user_data)
        except IntegrityError:
            return web.Response(
                content_type='application/json',
                text=json.dumps({'data': 'Username is already taken'})
            )
        return web.Response(
            content_type='application/json',
            text=json.dumps({'data': 'User successfully registered'})
        )


class AddVisitorView(BaseView):
    async def post(self):
        data = await self.request.post()
        _id = str(uuid.uuid4())
        visitor = {
            'id': _id,
            'name': data['name'],
            'time_in_timestamp': time.time(),
        }
        self.app['visitors'][_id] = visitor
        redirect(self.request, 'main')


class RemoveVisitorView(BaseView):
    @aiohttp_jinja2.template('remove_visitor.html')
    async def get(self):
        data = self.request.GET
        visitor_id = data['id']
        visitor = self.app['visitors'].get(visitor_id)
        if visitor is None:
            redirect(self.request, 'main')
        visitor['time_out_timestamp'] = time.time()
        visitor['time_delta'] = visitor['time_out_timestamp'] - visitor['time_in_timestamp']
        visitor['price'] = int(visitor['time_delta'] / 3600 * settings.HOUR_PRICE * 2) / 2
        return visitor

    async def post(self):
        data = await self.request.post()
        visitor_id = data['id']
        visitor = self.app['visitors'].pop(visitor_id, None)
        if visitor is None:
            return web.Response(
                content_type='application/json',
                text=json.dumps({'error': 'There is no visitor with such id'})
            )
        visitor.pop('id')
        visitor['paid'] = float(data['paid'])
        self.app['shift']['left_visitors'].append(visitor)
        self.app['shift']['nominal_cash'] += visitor['paid']
        self.app['shift']['income'] += visitor['paid']
        self.app['shift']['profit'] += visitor['paid']
        redirect(self.request, 'main')


class DischargeView(BaseView):
    async def post(self):
        data = await self.request.post()
        amount = float(data['amount'])
        self.app['shift']['nominal_cash'] -= amount
        self.app['shift']['outcome'] += amount
        self.app['shift']['profit'] -= amount
        discharge = {
            'timestamp': time.time(),
            'amount': amount,
            'reason': data['reason'],
        }
        self.app['shift']['discharges'].append(discharge)
        redirect(self.request, 'main')


class CloseShiftView(BaseView):
    @aiohttp_jinja2.template('close_shift.html')
    async def get(self):
        return {'shift': self.app['shift']}

    async def post(self):
        data = await self.request.post()
        real_cash = float(data['real_cash'])
        self.app['shift']['real_cash'] = real_cash
        self.app['shift']['user'] = self.app['user_id']
        self.app['cash'] = real_cash
        await close_shift(self.app['shift'], self.db)
        logout(self.request)


class StaticsView(BaseView):
    @aiohttp_jinja2.template('statistics.html')
    async def get(self):
        if not self.app.get('is_admin'):
            redirect(self.request, 'main')
        shifts = await get_shifts()
        return {'shifts': shifts}
