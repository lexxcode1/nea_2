from helper import row_exists
import models.bill as B


def bill_exists(bid, cur, db):
    bills = B.Bills(cur, db)
    return [b for b in bills.bills if b.id == bid] or not row_exists("bills", bid)


def add_customer_to_bill(bid, cid, cur, db):
    if not bill_exists(bid, cur, db):
        raise ValueError(f'Bill<{bid}> does not exist')

    bill = B.Bill(bid, cur, db)
    bill.customer_id = cid
