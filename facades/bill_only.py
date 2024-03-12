

"""
This file is used to avoid a circular import dependency between models.bill and models.customer
"""


def bill_exists(bid, cur, db):
    from helper import row_exists
    import models.bill as B
    bills = B.Bills(cur, db)
    return [b for b in bills.rows if b.sid == bid] or not row_exists("bills", bid)


def add_customer_to_bill(bid, cid, cur, db):
    import models.bill as B
    if not bill_exists(bid, cur, db):
        raise ValueError(f'Bill<{bid}> does not exist')

    bill = B.Bill(bid, cur, db)
    bill.customer_id = cid


def get_all_bills_by_seat(sid, cur, db):
    import models.bill as B
    bills = B.Bills(cur, db)
    return [b for b in bills.rows if b.sid == sid] or None


def get_all_bills_created_by_staff_member(staff_id, cur, db):
    import models.bill as B
    bills = B.Bills(cur, db)
    return bills.get(created_by_staff_id=staff_id) or None


def add_bill(cur, db, customer_id=None, seat_id=None, created_by_staff_id=None):
    import models.bill as B
    bills = B.Bills(cur, db)
    return bills.add(customer_id, seat_id, created_by_staff_id)
