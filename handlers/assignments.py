import random

from connector import connect
from models import StaffMember, Booking, Seat, Seats

# Connect to the database
db = connect()
cur = db.cursor()

def assign_staff_member_to_booking(
        on_shift: list[StaffMember],
        booking: Booking
) -> StaffMember | None:
    """
    Assign a staff member to a booking
    :param on_shift: list[StaffMember]: the staff members on shift
    :param booking: Booking: the booking
    :return: tuple[StaffMember | None, StaffBookings]: the staff member and the updated staff bookings
    """
    # Get the service staff on shift
    service_staff = [staff_member for staff_member in on_shift if
                     staff_member.role.name in ['server', 'supervisor', 'manager', 'superuser']]

    # If there is no service staff on shift, return
    if not service_staff:
        return None

    # Get the staff member with the least amount of bookings
    staff_member = min(service_staff, key=lambda x: len(x.assigned_bookings))

    # Add the booking to the staff members assigned bookings
    booking.assigned_staff_member = staff_member

    return staff_member


def assign_booking_to_seat(covers: int) -> Seat | None:
    seats = Seats(cur, db)
    # Get a random seat
    seat = random.choice(seats.get(status='empty', max_size=covers))

    # If there is no seats, handle
    if not seat:
        # Check if there is a seat with a max_size within 2 more than the covers
        seat = random.choice(seats.get(status='empty', max_size=covers + 2))

        # If there is still no seat, return None
        if not seat:
            return None

        return seat

    if covers > 10:
        # Create a new seat
        return seats.add(name=f'{len(seats.rows) + 1}', max_size=covers, flagged=False, status='empty',
                         seat_type='table')

    return seat
