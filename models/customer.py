from datetime import datetime
from sqlite3 import Error

from facades.bill_only import add_customer_to_bill
from helper import row_exists, table_exists, validate_types
from models.base import RowBase, TableBase


class Customer(RowBase):
    """
    Customer class for rows in the Customers table

    Properties
    ----------
    id : int
        unique id for each Customer
    name : str
        name of the Customer
    bills : list[Bill]
        bills associated with the Customer with a one-to-many relationship
    vip : bool
        whether the Customer is VIP or not
    created_at : datetime
        datetime when the Customer was created
    updated_at : datetime
        datetime when the Customer was last updated

    Methods
    -------
    name.setter:
        Updates the name of the Customer by ID
    vip.setter:
        Updates the VIP status of the Customer by ID
    bills.getter:
        Returns the bills associated with the Customer by ID

    """

    def __init__(self, cid: int, cur, db) -> None:
        """
        Constructor for the Customer class

        Only for use in the Customers class
        """

        # Set the attributes
        attributes = ['name', 'vip']

        # Call the super constructor
        super().__init__(cid, cur, db, 'customer', attributes)

    @property
    def cid(self) -> int:
        """
        Property initiation for the id
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Property initiation for the name
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Updates the name of the Customer by ID
        """
        # Validate types
        validate_types((new_name, str, 'new_name'))

        # If the name is not between 1 and 20 characters, raise a ValueError
        if not 1 <= len(new_name) <= 50:
            raise ValueError(f'Customer name must be between 1 and 50 characters, not {len(new_name)}')

        self.set_attribute('name', new_name)

    @property
    def vip(self) -> bool:
        """
        Property initiation for the VIP status
        """
        if type(self._vip) is int:
            return bool(self._vip)
        return self._vip

    @vip.setter
    def vip(self, new_vip: bool) -> None:
        """
        Updates the VIP status of the Customer by ID
        """
        print(new_vip)
        # Validate types
        validate_types([(new_vip, bool, 'new_vip')])

        self.set_attribute('vip', new_vip)

    @property
    def bills(self) -> list:
        """
        Returns the bills associated with the Customer by ID
        """
        self.cur.execute(f"""
               SELECT * FROM bill WHERE customer_id = {self.cid}
            """)
        return self.cur.fetchall() or []

    @bills.getter
    def bills(self) -> list:
        """
        Returns the bills associated with the Customer by ID
        """
        self.cur.execute(f"""
               SELECT * FROM bill WHERE customer_id = {self.cid}
            """)

        return self.cur.fetchall() or []

    def add_bill(self, new_bill_id: int) -> None:
        """
        Adds a bill to the Customer by ID
        """
        # If the bill does not exist, raise a ValueError
        if not row_exists("bill", new_bill_id):
            raise ValueError(f'Bill<{new_bill_id}> does not exist')

        add_customer_to_bill(new_bill_id, self.cid, self.cur, self.db)
        print(f'Bill<{new_bill_id}> added to Customer<{self.cid}>')

    def __eq__(self, other):
        """
        Equality method for the Customer class
        """
        # Check that other is an instance of Customer and that all attributes are equal
        return isinstance(other,
                          Customer) and self.cid == other.cid and self.name == other.name and self.vip == other.vip

    def __repr__(self) -> str:
        """
        Representation of the Customer class
        """
        return f'<Customer id={self.cid}, name="{self.name}", vip={self.vip}>'


class Customers(TableBase):
    """
    Customers class for the Customers table

    """

    def __init__(self, cur, db):
        super().__init__(cur, db, 'customer', Customer, 'cid')

    def create_table(self) -> None:
        """
        Creates the Customers table if it does not exist
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS customer (
                id integer PRIMARY KEY,
                name text NOT NULL,
                vip boolean DEFAULT FALSE,
                created_at timestamp DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
        print('Customer table created')


    def add(self, name: str, vip: bool):
        """
        Adds a customer to the Customers table
        :return int: id of the new customer
        """
        cid = self.cur.execute(f"""
                INSERT INTO customer (name, vip) VALUES (?, ?)
                """, (name, vip)).lastrowid
        new_customer = Customer(cid, self.cur, self.db)

        return new_customer

    def __repr__(self):
        return f'<Customers customers={self.rows[0:5]}...>'
