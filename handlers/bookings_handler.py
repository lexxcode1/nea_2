import random
from datetime import datetime
from typing import NoReturn

from connector import connect
from constants import ITEM_NOTES
from handlers.assignments import assign_staff_member_to_booking, assign_booking_to_seat
from handlers.stack import PriorityQueue
from helper import display, event_happens, get_weighted_random_number
from models import Booking, StaffMember, Seat, Items, Actions, Item, Bills, Bill

# Connect to the database
db = connect()
cur = db.cursor()

def distribute_bookings(bookings: list[Booking], n: int = 4) -> list[list[Booking]]:
    """
    Distribute the bookings into n sublists
    :param bookings: list[Booking]: the bookings
    :param n: int: the number of sublists
    :return: list[list[Booking]]: the sublists contained in a list
    """
    sublists = [[] for _ in range(n)]
    for i, item in enumerate(bookings):
        sublists[i % n].append(item)
    return sublists


def process_booking(booking: Booking, on_shift: list[StaffMember], active_bookings: PriorityQueue, bills: Bills,
                    time_string: str, actions: Actions) \
        -> PriorityQueue:
    """
    Process a booking and return the active bookings Queue
    :param booking: Booking: the booking to be processed
    :param on_shift: list[StaffMember]: the staff members on shift
    :param active_bookings: PriorityQueue: the active bookings
    :param bills: Bills: the bills table
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :param actions: Actions: the actions table
    :return: PriorityQueue: the active bookings
    """
    # Get the staff needed for the booking
    assigned_staff_member: StaffMember | None = assign_staff_member_to_booking(on_shift, booking)

    # If there is no staff member available, display
    if not assigned_staff_member:
        display(f'No staff members available for {booking.customer.name}\'s booking')
        return active_bookings

    # Display the staff member assigned to the booking
    display(f'{assigned_staff_member.name} has been assigned to {booking.customer.name}\'s booking')

    # Seat the booking
    seat = assign_booking_to_seat(booking.covers)

    # If there is no seat, display
    if not seat:
        display(f'No seats available for {booking.customer.name}\'s booking, they will have to wait...')
        return active_bookings

    # Set the status of the seat to occupied
    seat.status = 'waiting_for_order'

    # Create a new bill for the booking
    bill: Bill = bills.add(
        seating_id=seat.id,
        covers=booking.covers,
        created_by_staff_id=assigned_staff_member.id
    )

    # Add an action for the bill creation
    actions.add(bill.id, assigned_staff_member.id, True, 0, 'create', 'NULL')

    # Set the bill for the booking
    booking.bill = bill

    # Display that the booking has been seated
    display(
        f'{time_string}:{booking.customer.name} has been seated at {seat.name} by {assigned_staff_member.name}'
    )

    # Add the booking to active bookings stack
    active_bookings.push(booking, 1 if booking.customer.vip else 2)

    return active_bookings


def handle_dietary_requirement(booking: Booking, staff_member: StaffMember, time_string: str, dietary_req: str) -> None:
    """
    Handle a dietary requirement for a booking
    :param booking: Booking: the booking to be handled
    :param staff_member: StaffMember: the staff member handling the booking
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :param dietary_req: str: the dietary requirement
    :return: None
    """
    display(f'{time_string}: {booking.customer.name} is {dietary_req}')
    # Add a note to the bill
    booking.bill.add_items((None, dietary_req), staff_id=staff_member.id)


def handle_booking_comments(booking: Booking, assigned_staff_member: StaffMember, time_string: str,
                            items: Items) -> None | NoReturn:
    """
    Handle the comments in a booking
    :param booking: Booking: the booking to be handled
    :param assigned_staff_member: StaffMember: the staff member assigned to the booking
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :param items: Items: the items class
    :return: None | NoReturn
    """
    # If the booking has no comments, return None
    if not booking.comment:
        return None

    # If the booking is celebrating an anniversary, give them a free glass of sparkling wine
    if 'anniversary' in booking.comment.lower():
        # Display that the booking is celebrating their anniversary
        display(f'{time_string}: {booking.customer.name} is celebrating their anniversary')

        # Get the cheapest sparking wine
        sparkling_wine = min(items.get(description='sparkling wine'), key=lambda x: x.price)

        # Add the sparkling wine to the bill with a complimentary note which makes the price 0 when calculating the total
        booking.bill.add_items((sparkling_wine, 'complimentary'), staff_id=assigned_staff_member.id)

    # If someone in the booking has a dietary requirement, handle it
    for dietary_req in ['gluten free', 'vegetarian', 'vegan']:
        if dietary_req in booking.comment.lower():
            handle_dietary_requirement(booking, assigned_staff_member, time_string, dietary_req)

    # If the booking is celebrating a birthday, give them a free shot
    if 'birthday' in booking.comment.lower():
        # Get the cheapest shot
        shot = min(items.get(True, description='liquer'), key=lambda x: x.price)

        # Add the shot to the bill with a complimentary note which makes the price 0 when calculating the total
        booking.bill.add_items((shot, 'complimentary'), staff_id=assigned_staff_member.id)

        # Display that the booking is celebrating their birthday
        display(
            f'{time_string}: {booking.customer.name} is celebrating their birthday, they have been given a free shot of {shot.name}!'
        )

    # If the booking has a dog, display
    if 'has dog' in booking.comment.lower():
        display(f'{time_string}: {booking.customer.name} has a dog with them, woof... woof...')


def take_order(booking: Booking, seat: Seat, time_string: str) -> Bill:
    """
    Take the order for a booking
    :param booking: Booking: the booking to take the order for
    :param seat: Seat: the seat the booking is seated at
    :param mins: str: the minutes
    :return: Bill: the bill for the booking
    """
    # Get the assigned staff member
    assigned_staff_member: StaffMember = booking.assigned_staff_member

    # Init items class
    items: Items = Items(cur, db)

    # Get the time string for the booking
    items_to_add: list[tuple[Item, str]] = []

    # If the booking has a comment, handle it
    if booking.comment:
        handle_booking_comments(booking, assigned_staff_member, time_string, items)
    # Loop through the covers in the booking
    for cover in range(booking.covers):
        items_to_add = serve_customer(assigned_staff_member, booking, items, items_to_add, time_string)

    # Add the items to the bill
    booking.bill.add_items(items_to_add, staff_id=assigned_staff_member.id)

    # Set the status of the seat to okay
    seat.status = 'okay'

    # Display that the order has been taken
    display(f'{time_string}: {booking.customer.name}\'s order has been taken by {assigned_staff_member.name}')

    return booking.bill


def serve_customer(assigned_staff_member: StaffMember, booking: Booking, items: Items,
                   items_to_add: list[tuple[Item, str]],
                   time_string: str) -> list[tuple[Item, str]]:
    """
    Serves a customer and returns the items needed to be added to a bill
    :param assigned_staff_member: StaffMember: the staff member assigned with the booking
    :param booking: Booking: the booking
    :param items: Items: the items class
    :param items_to_add: list[tuple[Item, str]]: the items to add to the bill
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :return: list[tuple[Item, str]]: the items to add to the bill
    """
    # Get a random item from the menu
    item = get_item(items)

    # Set the default comment to NULL
    item_comment = 'NULL'

    # If the item has note event happens, set the item comment to a random note
    if event_happens('item_has_note'):
        item_comment = random.choice(ITEM_NOTES)

    # Add the item to the bill
    items_to_add.append((item, item_comment))

    # Display that the item has been added to the bill
    display(
        f'{time_string}: {item.name} has been added to {booking.customer.name}\'s bill by {assigned_staff_member.name}'
    )

    # Return the items to add
    return items_to_add


def get_item(items: Items) -> Item:
    """
    Get a random item from the menu, will be changed to adjust for previous rounds etc
    :param items: Items: the items class
    :return: Item: the item
    """
    # ! Will be changed for a more realistic approach
    return random.choice(items.get())


def pay_and_leave(active_bookings: PriorityQueue, assigned_staff_member: StaffMember, booking: Booking, seat: Seat,
                  time_string: str, actions: Actions) -> PriorityQueue:
    """
    When a booking is about to leave, get them to pay and then make the seat empty and the booking inactive
    :param active_bookings: PriorityQueue: the active bookings queue
    :param assigned_staff_member: StaffMember: the staff member assigned to the booking
    :param booking: Booking: the booking
    :param seat: Seat: the seat the booking is seated at
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :param actions: Actions: the actions class
    :return: PriorityQueue: the active bookings queue
    """
    # Get the bill total
    total = booking.bill.total

    # Determine whether they leave a tip
    if event_happens('customer_leaves_tip'):
        # Get a random tip percentage
        tip_percentage = get_weighted_random_number(0, 25, 10, 2)

        # Add the tip to the total
        total += total * (tip_percentage / 100)

        # Display that the booking has left a tip
        display(f'{time_string}: {booking.customer.name} has left a {tip_percentage}% tip')

    # Display that the booking has paid and left
    display(f'{time_string}: {booking.customer.name} has paid {total} and left')

    # Add an action for the payment
    actions.add(booking.bill.id, assigned_staff_member.id, True, 0, 'payment', 'NULL')

    # Set the status of the seat to empty
    seat.status = 'empty'

    # Set the booking to inactive
    booking.active = False

    # Remove the booking from the active bookings stack
    active_bookings.remove(booking)

    # Return the active bookings stack
    return active_bookings


def progress_bookings(active_bookings: PriorityQueue, on_shift: list[StaffMember],
                      time_string: str, actions: Actions) -> PriorityQueue:
    """
    Progress the bookings in the active bookings stack
    :param active_bookings: PriorityQueue: the active bookings stack
    :param on_shift: list[StaffMember]: the staff members on shift
    :param time_string: str: the time string for the booking with format HH:MM AM/PM
    :param actions: Actions: the actions class
    :return: PriorityQueue: the active bookings stack
    """
    # Change all the seat statuses in active_bookings where priority is 2 to needs_checking
    busy_bookings = [item[0] for item in active_bookings.queue if item[1] == 2]

    # Loop through the bookings who are currently busy
    for booking in busy_bookings:
        # Set the status of these seats to needs_checking
        booking.bill.seat.status = 'needs_checking'

    # Get the bookings that have been seated
    seated_bookings = [booking[0] for booking in active_bookings.queue]

    # Loop through the seated bookings
    for booking in seated_bookings:
        # Get the staff member assigned to the booking
        assigned_staff_member = booking.assigned_staff_member

        # If the staff member is not on shift, assign a new staff member to the booking
        if assigned_staff_member not in on_shift:
            assigned_staff_member = assign_staff_member_to_booking(on_shift, booking)

        # If there is no staff member assigned to the booking, return
        if not assigned_staff_member:
            return active_bookings

        # Get the seat the booking is seated at
        seat = booking.bill.seat

        # If the seat is not occupied, return
        if seat.status == 'waiting_for_order':
            # If the customer wants to order, take their order
            take_order(booking, seat, time_string)

            # Remove the booking from the active bookings stack
            active_bookings.pop()

            # Add the booking to the active bookings stack with a priority of 2
            active_bookings.push(booking, 2)

            # Return the active bookings stack
            return active_bookings

        if seat.status == 'needs_checking':
            # Determine whether they want another round
            if event_happens('customer_wants_another_round'):
                # If they do, take their order
                take_order(booking, seat, time_string)

                # Set the status of the seat to okay
                seat.status = 'okay'

                # Remove the booking from the active bookings stack
                active_bookings.pop()

                # Add the booking to the active bookings stack with a priority of 2
                active_bookings.push(booking, 2)

                # Return the active bookings stack
                return active_bookings

            # If they don't want another round, take their payment and remove them from the active bookings stack
            active_bookings = pay_and_leave(active_bookings, assigned_staff_member, booking, seat, time_string, actions)

        # Display that the booking has been served
        display(f'{time_string}:{booking.customer.name} has been served by {assigned_staff_member.name}')

        # Remove the booking from the active bookings stack
        active_bookings.pop()

    return active_bookings
