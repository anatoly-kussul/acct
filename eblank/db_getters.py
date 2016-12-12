from datetime import datetime

from peewee_async import execute

from eblank.models import Shift, Discharge, Visitor, User


async def get_shifts(start_timestamp=None, end_timestamp=None, user_id=None):
    shifts = []

    query = Shift.select(Shift, User).join(User).order_by(Shift.time_opened_timestamp.desc())

    expressions = []
    if start_timestamp:
        start_datetime = datetime.fromtimestamp(start_timestamp)
        expressions.append(Shift.time_opened_timestamp >= start_datetime)
    if end_timestamp:
        end_datetime = datetime.fromtimestamp(end_timestamp)
        expressions.append(Shift.time_opened_timestamp <= end_datetime)
    if user_id:
        expressions.append(Shift.user == user_id)

    if expressions:
        query.where(*expressions)

    db_shifts = await execute(query)

    for shift in db_shifts:
        shift_d = shift.to_dict()
        user = shift.user
        shift_d['user'] = user
        shifts.append(shift_d)

    return shifts


async def get_shift_info(shift_id):
    discharges_query = Discharge.select().where(Discharge.shift == shift_id)
    db_discharges = await execute(discharges_query)
    discharges = [discharge.to_dict() for discharge in db_discharges]

    visitors_query = Visitor.select().where(Visitor.shift == shift_id)
    db_visitors = await execute(visitors_query)
    visitors = [visitor.to_dict() for visitor in db_visitors]

    return {
        'visitors': visitors,
        'discharges': discharges,
    }
