# from models.customer import Customers
import models.customer as C

def get_customer(cid, cur, db):
    return C.Customers(cur, db).get(cid=cid)
