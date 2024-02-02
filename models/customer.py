from datetime import datetime
from sqlite3 import Error

from facades.add_customer_to_bill import add_customer_to_bill
from helper import row_exists, table_exists, validate_types


class Customer:
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
        self.cur = cur
        self.db = db

        self._id = cid
        try:
            self._name, self._vip, self._created_at, self._updated_at = self.cur.execute("""
                       SELECT name, vip, created_at, updated_at FROM customer WHERE id = ?
                   """, (self.cid,)).fetchone()
        except Error as error:
            print(f'Failed to fetch Customer<{self.cid}>: {error}')
        except TypeError:
            raise ValueError('Invalid Customer<{self.cid}>')

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
        # If the name is the same as the current name, do nothing
        if new_name == self.name:
            return


        # Validate types
        validate_types((new_name, str, 'new_name'))

        # If the name is not between 1 and 20 characters, raise a ValueError
        if not 1 <= len(new_name) <= 50:
            raise ValueError(f'Customer name must be between 1 and 50 characters, not {len(new_name)}')

        self.cur.execute(f"""
            UPDATE customer
            SET 
                name = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_name, datetime.now(), self.cid))
        self.db.commit()

        self._name = new_name
        print(f'Customer<{self.cid}> name updated')

    @property
    def vip(self) -> bool:
        """
        Property initiation for the VIP status
        """
        return self._vip

    @vip.setter
    def vip(self, new_vip: bool) -> None:
        """
        Updates the VIP status of the Customer by ID
        """
        # If the vip status is the same as the current vip status, do nothing
        if new_vip == self.vip:
            return

        # If the vip status is not a boolean, raise a TypeError
        if not isinstance(new_vip, bool):
            raise TypeError(f'Customer vip status must be a boolean, not {type(new_vip)}')

        self.cur.execute(f"""
            UPDATE customer 
            SET 
                vip = ?, 
                updated_at = ?
            WHERE id = ?
        """, (new_vip, datetime.now(), self.cid))
        self.db.commit()

        self._vip = new_vip
        print(f'Customer<{self.cid}> VIP status updated')

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

    @property
    def created_at(self) -> datetime:
        """
        Property initiation for the created_at datetime
        """
        return self.created_at

    @created_at.setter
    def created_at(self, new_created_at: datetime) -> None:
        """
        Assures that you can not update the created_at datetime
        """
        raise AttributeError("Cannot update created_at datetime")

    @property
    def updated_at(self) -> datetime:
        """
        Property initiation for the updated_at datetime
        """
        return self.updated_at

    @updated_at.setter
    def updated_at(self, new_updated_at: datetime) -> None:
        """
        Updates the updated_at datetime
        """
        self.cur.execute(f"""
            UPDATE customer 
            SET 
                updated_at = ?
            WHERE id = ?
        """, (new_updated_at, self.cid))
        self.db.commit()

        self._updated_at = new_updated_at
        print(f'Customer<{self.cid}> updated_at datetime updated')

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
        return f'<Customer id={self.cid}, name="{self._name}", vip={self.vip}>'


class Customers:
    """
    Customers class for the Customers table

    Properties
    ----------
    customers : list[Customer]
        list of all Customers in the Customers table

    Methods
    -------
    add:
        Adds a customer to the Customers table
    get:
        Returns a list of customers by name, vip status, or id
    delete:
        Deletes a customer from the Customers table by id
    __get_customer_by_id:
        Returns a customer by id
    __get_customers_by_name:
        Returns a list of customers by name
    __get_customers_by_vip:
        Returns a list of customers by vip status
    """

    def __init__(self, cur, db):
        self.db = db
        self.cur = cur
        if not table_exists("customer"):
            self.create_table()
        self._customers = [Customer(row[0], cur, db) for row in self.cur.execute("""
            SELECT id FROM customer
        """).fetchall()]

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

    @property
    def customers(self) -> list[Customer]:
        """
        Property initiation for the customers
        """
        return self._customers

    @customers.getter
    def customers(self) -> list[Customer]:
        """
        Returns the customers in table
        """
        return [Customer(row[0], self.cur, self.db) for row in self.cur.execute("""
            SELECT id FROM customer
        """).fetchall()]

    @customers.setter
    def customers(self, new_customers: list[Customer]) -> None:
        """
        Updates the customers in table
        """
        self._customers = new_customers

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
    # customers.get(name='John')
    def get(self, **kwargs) -> list[Customer] | Customer:

        if not kwargs:
            return self.customers

        # Extract kwargs
        key, value = next(iter(kwargs.items()))
        return [customer for customer in self.customers if getattr(customer, key) == value]

    def delete(self, cid: int):
        """
        Deletes a customer from the Customers table by id
        :param cid: id of the customer to delete
        """
        if not [c for c in self.customers if c.cid == cid] or not row_exists("customer", cid):
            raise ValueError(f'Customer<{cid}> does not exist')

        customer_to_delete = self.get(cid=cid)

        self.cur.execute(f"""
            DELETE FROM customer WHERE id = {cid}
        """)

        self.db.commit()

        self.customers = [c for c in self.customers if c.cid != cid]
        print(f'Customer<{cid}> deleted')

        return customer_to_delete[0]

    def clear(self):
        """
        Clears the Customers table
        """
        self.cur.execute("""
            DELETE FROM customer
        """)
        self.db.commit()
        self.customers = []
        print('Customer table cleared')

    def __repr__(self):
        return f'<Customers customers={self.customers[0:5]}>'
