import peewee

import settings

db = peewee.PostgresqlDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    username = peewee.CharField()
    password = peewee.CharField()
    is_admin = peewee.BooleanField()


class Shift(BaseModel):
    user = peewee.ForeignKeyField(User, related_name='shifts')
    nominal_cash = peewee.DoubleField()
    real_cash = peewee.DoubleField()
    income = peewee.DoubleField()
    outcome = peewee.DoubleField()
    profit = peewee.DoubleField()


class Visitor(BaseModel):
    name = peewee.CharField()
    time_in = peewee.TimeField()
    time_out = peewee.TimeField()
    time_delta = peewee.DoubleField()
    price = peewee.DoubleField()
    paid = peewee.DoubleField()
