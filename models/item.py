from sqlite3 import Connection, Cursor

from base import RowBase, TableBase
from helper import validate_types, row_exists, check_gte_0
from models.menuitem import MenuItems


class Item(RowBase):
    """
    Item class for the Item rows in the table
    """
    def __init__(self, iid: int, cur: Cursor, db: Connection) -> None:
        """
        Initialize the Item class

        :param iid: int : id of the Item
        :param cur: Cursor : database cursor
        :param db: Connection : database connection
        """

        # Set constant DEPARTMENTS
        self.DEPARTMENTS = ['drink', 'food', 'other']

        # Get all the attributes of the Item
        attributes = ['name', 'price', 'cost', 'vat', 'quantity', 'individual_volume', 'total_volume', 'department',
                      'description']

        # Initialize the RowBase
        super().__init__(iid, cur, db, 'item', attributes)

        # Set up MenuItems for the link table between Item and Menu
        self.__menu_items = MenuItems(cur, db)

        # Set the relationship variables
        self._menus = []

    @property
    def iid(self) -> int:
        """
        Get the id of the Item
        :return: int: id of the Item
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the name of the Item
        :return: str: name of the Item
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Set the name of the Item
        :param new_name: str: name of the Item
        :return: None
        """
        # Validate types
        validate_types([(new_name, str, 'new_name')])

        # If new_name is not between 0 and 25 characters, raise ValueError
        if len(new_name) < 1 or len(new_name) > 25:
            raise ValueError('new_name must be between 1 and 25 characters long')

        # Set the name of the Item
        self.set_attribute('name', new_name)

    @property
    def price(self) -> float:
        """
        Get the price of the Item
        :return: float: price of the Item
        """
        return self._price

    @price.setter
    def price(self, new_price: float | int) -> None:
        """
        Set the price of the Item
        :param new_price: float | int: price of the Item
        :return: None
        """
        # Convert int to float
        new_price = float(new_price) if type(new_price) is int else new_price

        # Validate types
        validate_types([(new_price, float, 'new_price')])

        # If new_price is less than 0, raise ValueError
        check_gte_0(new_price, 'new_price')

        # Set the price of the Item
        self.set_attribute('price', new_price)

    @property
    def cost(self) -> float:
        """
        Get the cost of the Item
        :return: float: cost of the Item
        """
        return self._cost

    @cost.setter
    def cost(self, new_cost: float) -> None:
        """
        Set the cost of the Item
        :param new_cost: float: cost of the Item
        :return: None
        """
        # Convert int to float
        new_cost = float(new_cost) if type(new_cost) is int else new_cost

        # Validate types
        validate_types([(new_cost, float, 'new_cost')])

        # If new_cost is less than 0, raise ValueError
        check_gte_0(new_cost, 'new_cost')

        # Set the cost of the Item
        self.set_attribute('cost', new_cost)

    @property
    def vat(self) -> float:
        """
        Get the vat (value added tax) of the Item
        :return: float: vat of the Item
        """
        return self._vat

    @vat.setter
    def vat(self, new_vat: float) -> None:
        """
        Set the vat of the Item
        :param new_vat: float: vat of the Item
        :return: None
        """
        # Convert int to float
        new_vat = float(new_vat) if type(new_vat) is int else new_vat

        # Validate types
        validate_types([(new_vat, float, 'new_vat')])

        # If new_vat is less than 0, raise ValueError
        check_gte_0(new_vat, 'new_vat')

        # Set the vat of the Item
        self.set_attribute('vat', new_vat)

    @property
    def quantity(self) -> int:
        """
        Get the quantity of the Item
        :return: int: quantity of the Item
        """
        return self._quantity

    @quantity.setter
    def quantity(self, new_quantity: int) -> None:
        """
        Set the quantity of the Item
        :param new_quantity: int: quantity of the Item
        :return: None
        """
        # Validate types
        validate_types([(new_quantity, int, 'new_quantity')])

        # If new_quantity is less than 0, raise ValueError
        check_gte_0(new_quantity, 'new_quantity')

        # Set the quantity of the Item
        self.set_attribute('quantity', new_quantity)

    @property
    def individual_volume(self) -> float:
        """
        Get the individual_volume of the Item
        :return: float: individual_volume of the Item
        """
        return self._individual_volume

    @individual_volume.setter
    def individual_volume(self, new_individual_volume: float) -> None:
        """
        Set the individual_volume of the Item
        :param new_individual_volume: float: individual_volume of the Item
        :return: None
        """
        # Convert int to float
        new_individual_volume = float(new_individual_volume) if type(
            new_individual_volume) is int else new_individual_volume

        # Validate types
        validate_types([(new_individual_volume, float, 'new_individual_volume')])

        # If new_individual_volume is less than 0, raise ValueError
        check_gte_0(new_individual_volume, 'new_individual_volume')

        # Set the individual_volume of the Item
        self.set_attribute('individual_volume', new_individual_volume)

    @property
    def total_volume(self) -> float:
        """
        Get the total_volume of the Item
        :return: float: total_volume of the Item
        """
        return self._total_volume

    @total_volume.setter
    def total_volume(self, new_total_volume: float) -> None:
        """
        Set the total_volume of the Item
        :param new_total_volume: float: total_volume of the Item
        :return: None
        """
        # Convert int to float
        new_total_volume = float(new_total_volume) if type(new_total_volume) is int else new_total_volume

        # Validate types
        validate_types([(new_total_volume, float, 'new_total_volume')])

        # If new_total_volume is less than 0, raise ValueError
        self.set_attribute('total_volume', new_total_volume)

    @property
    def department(self) -> str:
        """
        Get the department of the Item
        :return: str: department of the Item
        """
        return self._department

    @department.setter
    def department(self, new_department: str) -> None:
        """
        Set the department of the Item
        :param new_department: str: department of the Item
        :return: None
        """
        # Validate types
        validate_types([(new_department, str, 'new_department')])

        # If the department is not valid, raise ValueError
        if new_department.lower() not in self.DEPARTMENTS:
            raise ValueError(f'Department<{new_department}> is not valid')

        # Set the department of the Item
        self.set_attribute('department', new_department)

    @property
    def menus(self) -> list:
        """
        Get the menus of the Item
        :return: list: menus of the Item
        """
        return self.__menu_items.get(item_id=self.iid)

    def add_menu(self, menu_id: int) -> None:
        """
        Add a menu to the Item
        :param menu_id: int: id of the Menu to add
        :return: None
        """
        # Validate types
        validate_types([(menu_id, int, 'menu_id')])

        # If the menu does not exist, raise ValueError
        if not row_exists('menu', menu_id):
            raise ValueError(f'Menu<{menu_id}> does not exist')

        # If the menu_id is already in the menus, raise ValueError
        if self.__menu_items.get(menu_id=menu_id, item_id=self.iid):
            raise ValueError(f'Menu<{menu_id}> already has Item<{self.iid}>')

        # Add the menu_id to the menus
        self.__menu_items.add(menu_id, self.iid)

    def remove_menu(self, menu_id: int) -> None:
        """
        Remove a menu from the Item
        :param menu_id: int: id of the Menu to remove
        :return: None
        """
        # Validate types
        validate_types([(menu_id, int, 'menu_id')])

        # If the menu does not exist, raise ValueError
        if not row_exists('menu', menu_id):
            raise ValueError(f'Menu<{menu_id}> does not exist')

        # If the menu_id is not in the menus, return
        menu_item = self.__menu_items.get(menu_id=menu_id, item_id=self.iid)
        if not menu_item:
            return

        # Remove the menu_id from the menus
        self.__menu_items.delete(menu_item.mid)

    def __eq__(self, other):
        """
        Check if two Items are equal
        :param other: Item: other Item to compare
        :return: bool: True if the Items are equal, False otherwise
        """
        return self.iid == other.iid

    def __repr__(self):
        """
        String representation of the Item
        :return: str: string representation of the Item
        """
        return f'<Item id={self.iid}, name={self.name}, price={self.price}, vat={self.vat}, quantity={self.quantity}, ' \
               f'individual_volume={self.individual_volume}, total_volume={self.total_volume}>'


class Items(TableBase):
    """
    Items class for the Item table in the database
    """
    def create_table(self):
        """
        Create the Items table
        :return: None
        """
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS item (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                cost REAL,
                department TEXT,
                description TEXT,
                vat REAL DEFAULT 20.0,
                quantity INTEGER,
                individual_volume REAL DEFAULT 0.0,
                total_volume REAL DEFAULT 0.0
            ) 
        ''')

        self.db.commit()
        print('Items table created')

    def __init__(self, cur: Cursor, db: Connection) -> None:
        """
        Initialize the Items class
        :param cur: Cursor : database cursor
        :param db: Connection : database connection
        """
        # Set constant DEPARTMENTS
        self.DEPARTMENTS = ['drink', 'food', 'other']

        # Initialize the TableBase
        super().__init__(cur, db, 'item', Item, 'iid')

    def add(self, name: str, price: float, vat: float, quantity: int, individual_volume: float,
            total_volume: float, department: str, description: str) -> Item:
        """
        Add a new Item to the database
        :param name: str: name of the Item
        :param price: float: price of the Item
        :param vat: float: vat of the Item
        :param quantity: int: quantity of the Item
        :param individual_volume: float: individual_volume of the Item
        :param total_volume: float: total_volume of the Item
        :param department: str: department of the Item
        :param description: str: description of the Item
        :return: Item: new Item
        """
        # Validate inputs
        validate_types([(name, str, 'name'), (price, float, 'price'), (vat, float, 'vat'),
                        (quantity, int, 'quantity'), (individual_volume, float, 'individual_volume'),
                        (total_volume, float, 'total_volume'), (department, str, 'department'),
                        (description, str, 'description')])

        # If the department is not valid, raise ValueError
        if department.lower() not in self.DEPARTMENTS:
            raise ValueError(f'Department<{department}> is not valid')

        # If the item already exists, raise ValueError
        if self.get(name=name):
            raise ValueError(f'Item<{name}> already exists')

        non_zero_values = [(price, 'price'), (vat, 'vat'), (quantity, 'quantity'),
                           (individual_volume, 'individual_volume'),
                           (total_volume, 'total_volume')]

        for value, name in non_zero_values:
            check_gte_0(value, name)

        # Add the item to the Items table
        self.cur.execute('''
            INSERT INTO item (name, price, vat, quantity, individual_volume, total_volume, department, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, price, vat, quantity, individual_volume, total_volume, department, description))

        self.db.commit()
        print(f'Item<{name}> added')

        new_item = Item(self.cur.lastrowid, self.cur, self.db)

        return new_item

    def __repr__(self):
        """
        String representation of the Items
        :return: str: string representation of the Items
        """
        return f'<Items rows={self.rows[0:3]}...>'
