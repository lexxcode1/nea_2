"""
This file contains helper functions for the project
"""
import random

import numpy as np

from connector import connect
from constants import EVENT_CHANCES, BOOKING_COMMENTS, BOOKING_WEIGHTS
from models import Booking, StaffMembers, StaffMember, Roles

# Connect to the database
db = connect()
cur = db.cursor()


def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database

    :param table_name: str Name of the table to check
    :return bool : True if the table exists, False otherwise
    """

    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")

    return cur.fetchone() is not None


def row_exists(table_name: str, row_id: int) -> bool:
    """
    Check if a row exists in the database

    :param table_name: str Name of the table to check
    :param row_id: int ID of the row to check
    :return bool : True if the row exists, False otherwise
    """

    return True


def valid_variable(var):
    """
    Check if a variable is in the correct format
    :param var: tuple: Variable to check
    :return: bool: True if the variable is in the correct format, False otherwise
    """
    return isinstance(var, tuple) and len(var) is 3 and isinstance(var[2], str)


def validate_types(variables: list[tuple] | tuple):
    """
    Validate the types of variables
    :param variables: list[tuple] in form (var, var_type, var_name)
    :return:
    """
    # If variables is a tuple, check if it is in the correct format
    if isinstance(variables, tuple):
        if not valid_variable(variables):
            raise ValueError('variables must be in the format (var, var_type, var_name)')
        variables = [variables]

    # Check if variables is a list
    if not isinstance(variables, list):
        raise TypeError('variables must be a list of tuples')

    # Check if variables are in correct format
    if False in [valid_variable(var) for var in variables]:
        raise ValueError('variables must be in the format (var, var_type, var_name)')

    for var, var_type, var_name in variables:
        # Check if the variable is the correct type
        if not isinstance(var, var_type):
            raise TypeError(f'{var_name}<{var}> must be a {var_type.__name__}, not {type(var).__name__}')


def check_gte_0(value: int | float, name: str) -> None:
    """
    Check if a value is greater than or equal to 0
    :param value: int | float: Value to check
    :param name: str: Name of the value
    :return: None
    """
    if value < 0:
        raise ValueError(f'{name} cannot be less than 0')


def binary_search(data, target, left, right, target_attribute=None):
    """
    Perform a binary search on a sorted list of objects.
    :param data:
    :param target:
    :param left:
    :param right:
    :return:
    """

    if right >= left:
        mid = left + (right - left) // 2  # Calculate midpoint

        if getattr(data[mid], target_attribute) == target:
            return mid

        elif getattr(data[mid], target_attribute) > target:
            return binary_search(data, target, left, mid - 1, target_attribute)  # Search left half

        else:
            return binary_search(data, target, mid + 1, right, target_attribute)  # Search right half

    else:
        return -1  # Target not found


def walking_binary_search(data, target_attribute, target_value):
    """
    Finds all occurrences of a target value in a sorted list of objects.
    :param data:
    :param target_attribute:
    :param target_value:
    :return:
    """

    index = binary_search(data, target_value, 0, len(data) - 1, target_attribute)

    if index == -1:
        return []  # Not found

    result = [index]

    # Walk left
    i = index - 1
    while i >= 0 and getattr(data[i], target_attribute) == target_value:
        result.insert(0, i)
        i -= 1

    # Walk right
    i = index + 1
    while i < len(data) and getattr(data[i], target_attribute) == target_value:
        result.append(i)
        i += 1

    # return the data filtered with only the indexes
    return [data[i] for i in result]


def display(msg):
    return print(msg)


def get_weighted_random_number(low, high, weight, std_dev=1):
    """
    Get a weighted random number between low and high
    :param low: int: the low number
    :param high: int: the high number
    :param weight: int: the weight
    :param std_dev: int: the standard deviation
    :return: int: the weighted random number
    """
    # Create a normal distribution with mean weight and standard deviation std_dev
    normal_distribution = np.random.normal(weight, std_dev, 100)

    # Truncate the normal distribution to be between low and high
    truncated_normal_distribution = np.clip(normal_distribution, low, high)

    # Get a random number from the truncated normal distribution
    return random.choice(truncated_normal_distribution).round()


def event_happens(event: str) -> bool:
    """
    Check if an event happens
    :param: event: str: the event
    :return: bool: True if the event happens, False otherwise
    """
    if event not in EVENT_CHANCES:
        raise ValueError(f'{event} is not a valid event')

    return random.randint(1, 100) <= EVENT_CHANCES[event]


def choose_role():
    """
    Choose a role based on the given chances
      1. Server: 53%
      2. Bartender: 35%
      3. Supervisor: 10%
      4. Manager: 5%
      5. Superuser: 2%

    :return str: the role
    """

    # The chances of each role
    role_chances = {
        'server': 53,
        'bartender': 35,
        'supervisor': 10,
        'manager': 5,
        'superuser': 2
    }

    # Create a list of roles based on the chances
    roles = []
    for role, chances in role_chances.items():
        roles.extend([role] * chances)

    # Choose a random role
    return random.choice(roles)


def get_staff_needed(lunch_bookings: list[Booking], staff_members: StaffMembers, roles: Roles) -> list[StaffMember]:
    """
    Get the staff needed for the lunch service
    :param lunch_bookings: list[Bookings]: the bookings for lunch
    :param staff_members: StaffMembers: the staff members table
    :param roles: Roles: the roles table
    :return: int: the staff needed
    """

    # Create a list for the staff needed
    staff_needed = []

    # Get a member of staff to supervise
    supervising_staff = [staff_members.get(role_id=roles.get(name=role_name)[0].id) for role_name in
                         ['supervisor', 'manager', 'superuser']]

    # Add the supervising staff to the staff needed
    staff_needed.extend(supervising_staff)

    # Add a bartender for every 10 lunch bookings
    bartenders = [staff_members.get(role_id=roles.get(name='bartender')) for _ in range(len(lunch_bookings) // 10)]

    # Add the bartenders to the staff needed
    staff_needed.extend(bartenders)

    # Add a server for every 10 lunch bookings
    servers = [staff_members.get(role_id=roles.get(name='server')) for _ in range(len(lunch_bookings) // 10)]

    # Add the servers to the staff needed
    staff_needed.extend(servers)

    return staff_needed


def get_random_booking_comment():
    """
    Get a random booking comment
    :return: str: the random booking comment
    """
    return random.choices(BOOKING_COMMENTS, weights=BOOKING_WEIGHTS)[0]
