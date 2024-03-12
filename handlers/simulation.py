from datetime import datetime
from typing import NamedTuple

from freezegun import freeze_time

from connector import connect
from handlers.booking_generation import generate_bookings
from handlers.bookings_handler import distribute_bookings, progress_bookings, process_booking
from handlers.events import handle_hourly_events
from handlers.on_shift import handle_on_shift
from handlers.stack import PriorityQueue
from helper import display, get_staff_needed
from models import Bookings, Booking, StaffMember, StaffMembers, Actions, Bills, Customers, Roles

# Connect to the database
db = connect()
cur = db.cursor()

class StartDay(NamedTuple):
    """
    A named tuple for the start_day function
    """
    bookings: Bookings
    date: datetime
    bookings_for_day: list[Booking]
    lunch_staff: list[StaffMember]
    dinner_staff: list[StaffMember]


def start_day(staff_members: StaffMembers, customers: Customers, roles: Roles,
              date: datetime = datetime.now()) -> StartDay:
    """
    Start the day
    :return: StartDay: an object for accessing the returned variables
    """
    # Initiate the bookings table
    bookings = Bookings(cur, db)

    # Generate bookings for the day
    bookings_for_day = generate_bookings(date.strftime('%A'), date, bookings, customers)

    # Determine how many staff members are needed for lunch service
    lunch_bookings = [booking for booking in bookings_for_day if booking.date.hour < 15]

    # Get the staff members to clock in
    lunch_staff = get_staff_needed(lunch_bookings, staff_members, roles)

    # Determine how many staff members are needed for dinner service
    dinner_bookings = [booking for booking in bookings_for_day if booking.date.hour >= 15]

    # Get the staff members to clock in
    dinner_staff = get_staff_needed(dinner_bookings, staff_members, roles)

    # Return the StartDay object
    return StartDay(bookings, date, bookings_for_day, lunch_staff, dinner_staff)


def simulate_hour(
        bookings_for_day: list[Booking],
        lunch_staff: list[StaffMember],
        dinner_staff: list[StaffMember],
        actions: Actions = Actions(cur, db),
        bills: Bills = Bills(cur, db),
        staff_members: StaffMembers = StaffMembers(cur, db),
        uncompleted_bookings: list[Booking] = None
) -> list[Booking]:
    """
    Simulate an hour of the day at the bar
    :param bookings_for_day: list[Booking]: the bookings for the day
    :param lunch_staff: list[StaffMember]: the lunch staff
    :param dinner_staff: list[StaffMember]: the dinner staff
    :param actions: Actions: the actions table
    :param bills: Bills: the bills table
    :param staff_members: list[StaffMember]: the staff members table
    :param uncompleted_bookings: list[Booking]: the uncomplete bookings
    :return: list[Booking]: the uncomplete bookings
    """

    # If there are no uncomplete bookings, set it to an empty list
    if uncompleted_bookings is None:
        uncompleted_bookings = []

    # Get the bookings for this hour
    bookings_for_hour = [booking for booking in bookings_for_day if
                         booking.date.hour == datetime.now().hour]

    # All the staff currently on shift
    on_shift = []

    # Init active bookings queue
    active_bookings = PriorityQueue()

    # If there are any uncomplete bookings, add them to the active bookings queue with a priority of 1
    for booking in uncompleted_bookings:
        active_bookings.push(booking, 1)

    # Clock in and out staff
    on_shift = handle_on_shift(dinner_staff, lunch_staff, on_shift)

    # If there is no one clocked in, return
    if not on_shift:
        display('Everyones gone home...')
        return uncompleted_bookings

    on_shift, bookings_for_hour = handle_hourly_events(on_shift, bookings_for_hour, staff_members)

    # Split the bookings for the hour into 4 sub lists without numpy
    bookings_for_hour = distribute_bookings(bookings_for_hour, 4)

    # Display the bookings for the hour
    display("Whilst we've been looking at the back end, the following has happened:")

    # Loop through the bookings for the hour
    for i, interval in enumerate(bookings_for_hour):
        # Create a time string
        time_string = f'{datetime.now().hour}:{i * 15} {datetime.now().strftime("%p")}'

        # Progress 4 of the active bookings
        active_bookings = progress_bookings(active_bookings, on_shift,
                                            time_string, actions)
        for booking in interval:
            active_bookings = process_booking(booking, on_shift, active_bookings, bills, time_string, actions)

    # Set uncomplete bookings to the remaining active bookings
    uncompleted_bookings = [active_bookings.pop() for _ in range(len(active_bookings))]

    # If there is still hours left in the day, recursively rerun the simulation
    if datetime.now().hour > 23:
        # After the last hour, first process any uncomplete bookings
        for booking in uncompleted_bookings:
            time_string = f'{datetime.now().hour}:00 {datetime.now().strftime("%p")}'
            active_bookings = process_booking(booking, on_shift, active_bookings, bills, time_string, actions)

        # After all bookings are handled, clock out all staff
        for staff in on_shift:
            staff.end_shift()
            display(f'{staff.name} has clocked out from their shift!')

        display('The bar has now closed, time to go home!')

        return uncompleted_bookings

    return uncompleted_bookings


def simulate_day(staff_members: StaffMembers, customers: Customers, actions: Actions, bills: Bills, roles: Roles,
                 date: datetime = datetime.now()):
    # Determine chances for events
    day = start_day(staff_members, customers, roles, date)

    # Init uncomplete bookings
    uncompleted_bookings = []

    # Loop through hours in the range [12:00pm, 11:00pm]
    for hr in range(12, 24):
        with freeze_time(day.date.replace(hour=hr, minute=0, second=0)):
            uncompleted_bookings = simulate_hour(
                day.bookings_for_day,
                day.lunch_staff,
                day.dinner_staff,
                actions,
                bills,
                staff_members,
                uncompleted_bookings
            )
