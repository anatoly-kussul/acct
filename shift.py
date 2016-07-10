import time

from models import Shift, Visitor, Discharge


def open_shift(cash=0):
    shift = {
        'nominal_cash': cash,
        'income': 0,
        'outcome': 0,
        'profit': 0,
        'time_opened': time.time(),
        'discharges': [],
        'left_visitors': [],
    }
    return shift


async def close_shift(shift, db):
    left_visitors = shift.pop('left_visitors')
    discharges = shift.pop('discharges')
    shift['time_close'] = time.time()
    shift_db = await db.create(Shift, **shift)
    for visitor in left_visitors:
        await db.create(Visitor, shift=shift_db, **visitor)
    for discharge in discharges:
        await db.create(Discharge, shift=shift_db, **discharge)
