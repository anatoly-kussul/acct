import time

from models import Shift, Visitor, Discharge


async def shift_db_to_dict(shift_db, db):
    def discharge_to_dict(discharge_db):
        return {
            'amount': discharge_db.amount,
            'reason': discharge_db.reason,
            'time': discharge_db.time,
        }

    def visitor_to_dict(visitor_db):
        return {
            'name': visitor_db.name,
            'time_in': visitor_db.time_in,
            'time_out': visitor_db.time_out,
            'time_delta': visitor_db.time_delta,
            'price': visitor_db.price,
            'paid': visitor_db.paid,
        }

    discharges_db = await db.execute(shift_db.discharges)
    discharges = [discharge_to_dict(discharge_db) for discharge_db in discharges_db]
    visitors_db = await db.execute(shift_db.visitors)
    visitors_left = [visitor_to_dict(visitor_db) for visitor_db in visitors_db]
    print(shift_db.visitors)
    print(visitors_left)

    shift = {
        'username': shift_db.user.username,
        'nominal_cash': shift_db.nominal_cash,
        'real_cash': shift_db.real_cash,
        'income': shift_db.income,
        'outcome': shift_db.outcome,
        'profit': shift_db.profit,
        'time_opened': shift_db.time_opened,
        'time_close': shift_db.time_close,
        'discharges': discharges,
        'visitors_left': visitors_left,
    }
    return shift


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
