import random
from datetime import datetime

import numpy as np

from helper import event_happens, get_random_booking_comment
from models import Bookings, Booking, Customers


def generate_bookings(day_of_the_week: str, date: datetime, bookings: Bookings, customers: Customers) -> list[Booking]:
    """
    Generate bookings for the day of the week
    :param day_of_the_week: str: the day of the week
    :param date: datetime: the date
    :param bookings: Bookings: the bookings class
    :param customers: Customers: the customers class
    :return: object: the bookings
    """
    # Normalise day_of_the_week
    day_of_the_week = day_of_the_week.lower().strip()

    # If day_of_the_week is not a valid day of the week, raise a ValueError
    if day_of_the_week not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        raise ValueError(f'{day_of_the_week} is not a valid day of the week')

    if day_of_the_week in ['friday', 'saturday']:
        # Get a random number between 6 and 25 for the amount of bookings
        amount_of_bookings = random.randint(6, 25)
    else:
        # Get a random number between 0 and 10 for the amount of bookings
        amount_of_bookings = random.randint(0, 10)

    # Check if the date matches the day_of_the_week
    if date.strftime('%A').lower() != day_of_the_week:
        raise ValueError(f'{date} is not a {day_of_the_week}')

    for _ in range(amount_of_bookings):
        # Generate a poisson distribution for the amount of covers
        cover_poisson = np.random.poisson(4, 100)

        # Clip the poisson distribution to be between 0 and 15
        cover_poisson = np.clip(cover_poisson, 0, 15)

        # Get a random number from the poisson distribution
        covers = random.choice(cover_poisson)

        # Get a random customer
        customer = random.choice(customers.get())

        # Get a random time between 12:00 and 20:00, with a 1:2 chance of being between 12:00 and 14:00
        booking_time = random.choice([random.randint(1200, 1400), random.randint(1800, 2000) * 2])

        # Round to the nearest multiple of 15
        booking_time = round(booking_time / 15) * 15

        date = date.replace(hour=booking_time // 100, minute=booking_time % 100, second=0)

        # Set to a string
        comment = ''

        # If the booking should have a comment (EVENT_CHANCES['booking_has_comment']% CHANCE) then add a comment
        if event_happens('booking_has_comment'):
            comment = get_random_booking_comment()

        # If the customer is a VIP, add to comment
        if customer.vip:
            comment = f'{comment} VIP' if comment else 'VIP'

        # Add the booking
        bookings.add(
            date=date,
            covers=covers,
            customer=customer,
            comment=comment
        )

    # Get bookings for day
    bookings_for_day = bookings.get(date_between=(date, date.replace(hour=23, minute=59, second=59)))

    return bookings_for_day
