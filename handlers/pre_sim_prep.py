import re
import time

from faker import Faker

from helper import get_weighted_random_number
from models import Roles, StaffMembers, Items, Menus, Seats, Customers
from connector import connect
import random

db = connect()

cur = db.cursor()

fake = Faker()


# Create the roles
def create_roles():
    """
    Create the roles server, bartender, supervisor, manager, superuser
    :return Roles: the roles
    """

    # Create the roles
    roles = Roles(cur, db)  # Init creates initial roles

    return roles


# Create the staff members
def create_staff_members(roles):
    """
    Create 15 staff members with random names and roles
    :param roles: the roles class
    :return: StaffMembers: the staff members class
    """

    # Create the staff members
    staff_members = StaffMembers(cur, db)

    if len(staff_members.rows) > 15:
        return staff_members

    # Add 15 staff members
    for _ in range(15):
        staff_members.add(
            name=fake.first_name(),
            role_id=roles.get(name=choose_role())[0].id,
            wage=random.randint(1000, 2000) / 100,
        )

    # Add 15 staff members
    return staff_members


def get_price(cost: float) -> float:
    """
    Get the price of an item based on the cost price and a normal distribution of GP%
    :param cost: the cost price
    :return float: the price
    """

    # Get the gross profit percentage (GP%)
    gp_percentage = get_weighted_random_number(50, 90, 70, 5)

    # Get the price
    price = cost / (1 - gp_percentage)

    # Round the price to 2 decimal places
    return round(price, 2)


def create_items():
    """
    Create the items from the items-sheet.csv file
    :return: Items: the items class
    """
    items_table = Items(cur, db)

    # If there's already enough items, return
    if len(items_table.rows) > 150:
        return items_table

    # Import items-sheet.csv
    with open('items-sheet.csv', 'r') as file:
        items = file.readlines()
        # Get the headers and remove the newline character
        headers = items[0].strip().split(',')
        # Remove the headers from the items list
        items = items[1:]

        # Get the data from the items list
        for item in items:
            data = item.strip().split(',')
            # Create the item Description,Name,Size,Units in size,Cost price
            description, name, size, units_per_size, cost = data

            # Remove empty rows and rows with no name
            if not name:
                continue

            # Clean the data
            description = description.strip().lower()
            name = name.replace('*', '').strip().lower()
            size = size.strip().lower()

            # If the item already exists, skip it
            if items_table.get(True, name=name):
                continue

            if units_per_size == '':
                units_per_size = 1

            units_per_size = int(units_per_size)

            # Write a regex to remove all non-numeric characters from the cost
            cost = re.sub(r'[^0-9.]', '', cost)

            cost = float(cost) if cost else 0

            # Sort the sizes out
            if size == 'bot':
                size = 750
            elif 'ml' in size:
                size = int(size.replace('ml', ''))
            elif 'cl' in size:
                size = int(size.replace('cl', '')) * 10
            elif 'l' in size:
                size = int(size[0:size.index('l')]) * 1000
            else:
                size = 0

            # Add the item
            items_table.add(
                name=name,
                price=get_price(cost),  # Get the price (based on the cost price and a normal distribution of GP%)
                cost=cost,
                vat=0.2,
                quantity=random.randint(10, 100),
                individual_volume=size,
                total_volume=size * units_per_size,
                department='drink',
                description=description
            )

    return items_table


def create_menus():
    """
    Create the menus draught, bottles, spirits, wine, soft, liquer, apertif, digestif, low-alc, other
    :return: Menus: the menus class
    """

    # Create the menus table
    menus = Menus(cur, db)

    # The names of the menus
    names = ['draught', 'bottles', 'spirits', 'wine', 'soft', 'liquer', 'apertif', 'digestif', 'low-alc', 'other']

    # Add the menus
    for name in names:
        if len(menus.get(name=name)) > 0:
            print(f'Skipping {name}')
            continue
        menus.add(name=name, active=True, max_size=40)

    # Return the menus
    return menus


def create_menu_items(menus, items):
    """
    Assign items to menus
    :param menus: Menus: the menus class
    :param items: Items: the items class
    :return: Menus: the menus class
    """

    # The description to menu mapping
    description_to_menu = {
        'draught': ['draught beer'],
        'bottles': ['bottled beer', 'cider'],
        'spirits': ['vodka', 'rum', 'whiskey', 'brandy', 'tequila'],
        'wine': ['red wine', 'white wine', 'rose wine', 'sparkling wine'],
        'soft': ['soft drinks'],
        'liquer': ['liquer'],
        'apertif': ['absinthe', 'vermouth', 'sherry'],
        'digestif': ['port', 'desert wine'],
        'low-alc': ['non alcoholic spirits', 'non alcohol'],
        'other': ['misc']
    }

    # Assign items to menus
    for menu, descriptions in description_to_menu.items():
        for description in descriptions:
            for item in items.get(description=description):
                print(f'{menus.get(name=menu)[0].name}: {item.name} <{item.id}>')
                menus.get(name=menu)[0].add_item(item.id)

    return menus


def create_seats():
    """
    Create and add 10 seats to the Seats table
    :return:
    """

    # Create the seats table
    seats = Seats(cur, db)

    # The chances of each seat type
    seat_chances = {
        'table': 40,
        'booth': 30,
        'bar': 10,
        'high-table': 20
    }

    # Create a list of seat types based on the chances
    types = []
    for seat_type, chances in seat_chances.items():
        types.extend([seat_type] * chances)

    # Set seat_type
    seat_type = random.choice(types)

    # Set max_size
    max_size = get_weighted_random_number(0, 15, 4, std_dev=2) if seat_type != 'bar' else 1

    # Add 10 seats
    for i in range(1, 11):
        seats.add(name=f'{i}', max_size=max_size, flagged=False, status='empty',
                  seat_type=seat_type)

    # Add 10 seats
    return seats


def create_customers():
    """
    Create and add 40 customers to the Customers table
    :return Customers: the customers class
    """

    # Create the customers table
    customers = Customers(cur, db)
    for _ in range(40):
        # Set the vip status to True for 10% of the customers
        customers.add(name=fake.first_name(), vip=random.choice([True] * 10 + [False] * 90))

    # Add 40 customers
    return customers


def simulation_prep():
    # Create the roles
    print('Creating roles')
    roles = create_roles()
    print(roles)

    # Create the staff members
    print('Creating staff members')
    staff_members = create_staff_members(roles)

    # Create the items
    print('Creating items')
    items = create_items()

    # Create the menus
    print('Creating menus')
    menus = create_menus()

    # Assign items to menus
    print('Assigning items to menus')
    create_menu_items(menus, items)

    # Create the seats
    print('Creating seats')
    seats = create_seats()

    # Create the customers
    print('Creating customers')
    customers = create_customers()

    return roles, staff_members, items, menus, seats, customers