import models.seating as S

"""
This file is used to avoid a circular import dependency between other models and models.seat
"""



def get_seat(sid, cur, db):
    return S.Seats(cur, db).get(sid=sid)[0]