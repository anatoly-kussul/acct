import datetime
import logging
from hashlib import md5

import peewee
import peewee_async
from playhouse.shortcuts import model_to_dict, dict_to_model

from eblank import settings

db = peewee_async.PostgresqlDatabase(
    autocommit=True,
    autorollback=True,
    **settings.POSTGRES_CONNECTION_SETTINGS
)


def dict_timestamp_to_datetime(data):
    return {
        key: datetime.datetime.fromtimestamp(value) if ('timestamp' in key and isinstance(value, float)) else value
        for key, value in data.items()
        }


def dict_datetime_to_timestamp(data):
    return {
        key: value.timestamp() if isinstance(value, datetime.datetime) else value
        for key, value in data.items()
        }


class BaseModel(peewee.Model):
    class Meta:
        database = db

    def to_dict(self):
        model_dict = model_to_dict(self, backrefs=False, recurse=False)
        model_dict = dict_datetime_to_timestamp(model_dict)
        for field in self._meta.sorted_fields:
            if isinstance(field, peewee.ForeignKeyField):
                model_dict.pop(field.name)
        return model_dict

    @classmethod
    def from_dict(cls, data):
        data = dict_timestamp_to_datetime(data)
        return dict_to_model(cls, data)


class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    is_admin = peewee.BooleanField()


class Shift(BaseModel):
    user = peewee.ForeignKeyField(User, related_name='shifts')
    time_opened_timestamp = peewee.DateTimeField(index=True)
    time_close_timestamp = peewee.DateTimeField(index=True)
    nominal_cash = peewee.DoubleField()
    real_cash = peewee.DoubleField()
    income = peewee.DoubleField()
    outcome = peewee.DoubleField()
    profit = peewee.DoubleField()


class Visitor(BaseModel):
    shift = peewee.ForeignKeyField(Shift, related_name='visitors')
    name = peewee.CharField()
    time_in_timestamp = peewee.DateTimeField()
    time_out_timestamp = peewee.DateTimeField()
    time_delta = peewee.DoubleField()
    price = peewee.DoubleField()
    paid = peewee.DoubleField()


class Discharge(BaseModel):
    shift = peewee.ForeignKeyField(Shift, related_name='discharges')
    amount = peewee.FloatField()
    timestamp = peewee.DateTimeField()
    reason = peewee.TextField()


def drop_tables():
    db.connect()
    User.drop_table(fail_silently=True, cascade=True)
    Shift.drop_table(fail_silently=True, cascade=True)
    Visitor.drop_table(fail_silently=True, cascade=True)
    Discharge.drop_table(fail_silently=True, cascade=True)
    db.close()


def create_tables():
    db.connect()
    db.create_tables([User, Shift, Visitor, Discharge], safe=True)


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
