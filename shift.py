import time

from models import Shift, Visitor, Discharge, dict_timestamp_to_datetime


def open_shift(cash=0):
    shift = {
        'nominal_cash': cash,
        'income': 0,
        'outcome': 0,
        'profit': 0,
        'time_opened_timestamp': time.time(),
        'discharges': [],
        'left_visitors': [],
    }
    return shift


async def close_shift(shift, db):
    left_visitors = shift.pop('left_visitors')
    discharges = shift.pop('discharges')
    shift['time_close_timestamp'] = time.time()
    shift_db = await db.create(Shift, **dict_timestamp_to_datetime(shift))
    for visitor in left_visitors:
        await db.create(Visitor, shift=shift_db, **dict_timestamp_to_datetime(visitor))
    for discharge in discharges:
        await db.create(Discharge, shift=shift_db, **dict_timestamp_to_datetime(discharge))
