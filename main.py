from datetime import datetime

from connector import connect
from handlers.pre_sim_prep import simulation_prep
from handlers.simulation import simulate_day
from models import Shifts, Actions, Bills

# Connect to the database
db = connect()
cur = db.cursor()

if __name__ == '__main__':
    # Fill out tables pre simulation
    roles, staff_members, items, menus, seats, customers = simulation_prep()

    # Initiate the shifts table
    shifts = Shifts(cur, db)

    # Initiate the actions table
    actions = Actions(cur, db)

    # Initiate the bills table
    bills = Bills(cur, db)

    # Simulate one day
    simulate_day(staff_members, customers, actions, bills, roles, date=datetime.now())
