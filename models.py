from hashlib import md5
import logging

import peewee_async
import peewee

import settings

db = peewee_async.PostgresqlDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    autocommit=True,
    autorollback=True,
)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    is_admin = peewee.BooleanField()


class Shift(BaseModel):
    user = peewee.ForeignKeyField(User, related_name='shifts')
    time_opened = peewee.DoubleField()
    time_close = peewee.DoubleField()
    nominal_cash = peewee.DoubleField()
    real_cash = peewee.DoubleField()
    income = peewee.DoubleField()
    outcome = peewee.DoubleField()
    profit = peewee.DoubleField()


class Visitor(BaseModel):
    name = peewee.CharField()
    time_in = peewee.DoubleField()
    time_out = peewee.DoubleField()
    time_delta = peewee.DoubleField()
    price = peewee.DoubleField()
    paid = peewee.DoubleField()


def drop_tables():
    db.connect()
    User.drop_table(fail_silently=True, cascade=True)
    Shift.drop_table(fail_silently=True, cascade=True)
    Visitor.drop_table(fail_silently=True, cascade=True)
    db.close()


def create_tables():
    db.connect()
    db.create_tables([User, Shift, Visitor], safe=True)


def add_fixtures():
    try:
        User.create(username='admin', password=md5('admin'.encode('utf-8')).hexdigest(), is_admin=True)
    except peewee.IntegrityError:
        logging.debug('admin user already exists')


def init_db(drop=False):
    if drop:
        drop_tables()
    create_tables()
    add_fixtures()
    async_db = peewee_async.Manager(db)
    async_db.allow_sync = False
    return async_db
