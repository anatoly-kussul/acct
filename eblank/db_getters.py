from datetime import datetime

from peewee_async import prefetch

from eblank.models import Shift, Discharge, Visitor


async def get_shifts(start_timestamp=None, end_timestamp=None, user_id=None):
    shifts = []

    query = Shift.select()

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

    discharges = Discharge.select().order_by(Discharge.timestamp)
    visitors = Visitor.select().order_by(Visitor.time_out_timestamp)

    db_shifts = await prefetch(query, discharges, visitors)

    for shift in db_shifts:
        shift_d = shift.to_dict()
        shift_d['discharges'] = [discharge.to_dict() for discharge in shift.discharges_prefetch]
        shift_d['visitors_left'] = [visitor.to_dict() for visitor in shift.visitors_prefetch]
        shifts.append(shift_d)

    return shifts
