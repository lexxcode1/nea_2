# from models.customer import Customers
import models.customer as C

"""
This file is used to avoid a circular import dependency between models.bill and models.customer
"""


def get_customer(cid, cur, db):
    return C.Customers(cur, db).get(cid=cid)[0]
