import time
from datetime import datetime

from helper import display
from models import StaffMember


def handle_on_shift(dinner_staff: list[StaffMember], lunch_staff: list[StaffMember], on_shift: list[StaffMember]) \
        -> list[StaffMember]:
    """
    This function handles the clocking in and out of staff members
    :param dinner_staff: list[StaffMember]: The dinner staff
    :param lunch_staff: list[StaffMember]: The lunch staff
    :param on_shift: list[StaffMember]: The staff members currently on shift
    :return: list[StaffMember]: The staff members now on shift
    """
    # If the hour is 12:00PM, clock in the lunch staff
    if datetime.now().hour == 12:
        for staff in lunch_staff:
            staff.start_shift()
            display(f'{staff.name} has clocked in for lunch service!')
            on_shift.append(staff)
            time.sleep(1)
    # If the hour is 3:00PM, clock in the dinner staff and clock out the lunch staff
    if datetime.now().hour == 15:
        for staff_in, staff_out in (dinner_staff, lunch_staff):
            # Clock the new member of staff in
            staff_in.start_shift()
            display(f'{staff_in.name} has clocked in for dinner service!')
            on_shift.append(staff_in)

            # Clock the old member of staff out
            staff_out.end_shift()
            display(f'{staff_out.name} has clocked out from lunch service!')
            on_shift.remove(staff_out)
            time.sleep(1)
    # If the hour is 11:00PM, clock out the dinner staff
    if datetime.now().hour == 23:
        for staff in dinner_staff:
            # Clock the member of staff out
            staff.end_shift()
            display(f'{staff.name} has clocked out from dinner service!')
            on_shift.remove(staff)
        display('The bar has now closed, time to go home!')

    return on_shift