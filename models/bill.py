from datetime import datetime
from sqlite3 import OperationalError, Cursor, Connection

from facades.get_customer import get_customer
from helper import row_exists, table_exists, validate_types


class Bill:
    """
    Bill class for rows in the Bills table
    
    """

    def __init__(self, bid: int, cur: Cursor, db: Connection) -> None:
        """
        Constructor for the Bill class
        
        Only for use in the Bills class
        """
        # If cur or db is None, raise a TypeError
        if cur is None or db is None:
            raise TypeError(f'Cursor and database cannot be None')

        validate_types([(bid, int, 'bid'), (cur, Cursor, 'cur'), (db, Connection, 'db')])

        # If cur is not connected to db, raise a ValueError
        if cur.connection is not db:
            raise ValueError(f'Cursor is not connected to database')

        self.db = db
        self.cur = cur

        # Initiate relationship variables
        self._customer = None
        self._seating = None
        self._created_by_staff = None

        if not row_exists('bill', bid):
            raise ValueError(f'Bill<{bid}> does not exist')

        self._id = bid

        attributes = ['customer_id', 'seating_id', 'total', 'covers', 'created_at', 'created_by_staff_id', 'updated_at']
        query = f"SELECT {', '.join(attributes)} FROM bill WHERE id = {self._id}"
        (self._customer_id,
         self._seating_id,
         self._total,
         self._covers,
         self._created_at,
         self._created_by_staff_id,
         self._updated_at) = self.cur.execute(query).fetchone()

    @property
    def bid(self) -> int:
        """
        Property initiation for the id
        """
        return self._id

    @property
    def customer_id(self) -> int:
        """
        Property initiation for the customer_id
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, new_cid: int | None) -> None:
        """
        Updates the customer_id of the Bill by ID
        """

        # If the customer_id is None, set it to NULL
        if new_cid is None:
            new_cid = 'NULL',
            self._customer_id = None
        else:
            validate_types([(new_cid, int, 'new_cid')])

        # If the customer_id is not None, check if the customer exists
        if not get_customer(cid=new_cid, cur=self.cur, db=self.db):
            raise ValueError(f'Customer<{new_cid}> does not exist')

        # If new_cid is valid, update the customer_id
        self.cur.execute(f"""
            UPDATE bill
            SET
                customer_id = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_cid, datetime.now(), self.bid))
        self.db.commit()

        self._customer_id = new_cid
        print(f'Bill<{self.bid}> customer_id updated')

    @property
    def customer(self):
        """
        Property initiation for the customer
        """
        return self._customer

    @customer.getter
    def customer(self):
        """
        Getter for the customer
        """
        try:
            return get_customer(cid=self.customer_id, cur=self.cur, db=self.db)
        except ValueError:
            return None

    @customer.setter
    def customer(self, new_customer):
        """
        Setter for the customer based on Customer class
        :param new_customer: Customer
        :return: None
        """
        # If the new_customer is None, set customer_id to None
        self.customer_id = new_customer.id if new_customer is not None else None

    @property
    def seating_id(self) -> int:
        """
        Property initiation for the table_id
        """
        return self._seating_id

    @seating_id.setter
    def seating_id(self, new_sid: int | None) -> None:
        """
        Updates the table_id of the Bill by ID
        """
        types_to_valid = []

        # If the new_tid is None, set it to NULL
        if new_sid is None:
            new_sid = 'NULL'
            self._seating_id = None
        else: types_to_valid.append((new_sid, int, 'new_sid'))


        # If new_tid is not None or int, raise a TypeError
        validate_types(types_to_valid)

        # TODO If new_tid is not an existing table, raise a ValueError

        self.cur.execute(f"""
            UPDATE bill 
            SET 
                seating_id = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_sid, datetime.now(), self.bid))
        self.db.commit()

        self._seating_id = new_sid if not None else None
        print(f'Bill<{self.bid}> table_id updated')

    @property
    def seating(self):
        return self._seating

    @seating.getter
    def seating(self):
        pass

    @seating.setter
    def seating(self, new_tid):
        pass

    @property
    def total(self) -> float:
        """
        Property initiation for the total
        """
        return self._total

    @total.setter
    def total(self, new_total: float) -> None:
        """
        Updates the total of the Bill by ID
        """
        validate_types([(new_total, float, 'new_total')])

        # If new_total is negative, raise a ValueError
        if new_total < 0:
            raise ValueError(f'Total must be positive, not {new_total}')

        # If new_total is valid, update the total
        self.cur.execute(f"""
            UPDATE bill 
            SET 
                total = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_total, datetime.now(), self.bid))
        self.db.commit()

        self._total = new_total
        print(f'Bill<{self.bid}> total updated')

    @property
    def covers(self) -> int:
        """
        Property initiation for the covers
        """
        return self._covers

    @covers.setter
    def covers(self, new_covers: int) -> None:
        """
        Updates the covers of the Bill by ID
        """

        validate_types([(new_covers, int, 'new_covers')])

        # If new_covers is greater than 999 or less than 0, raise a ValueError
        if new_covers > 999 or new_covers < 0:
            raise ValueError(f'Covers must be between 0 and 999, not {new_covers}')

        # If new_covers is valid, update the covers
        self.cur.execute(f"""
            UPDATE bill 
            SET 
                covers = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_covers, datetime.now(), self.bid))
        self.db.commit()

        self._covers = new_covers
        print(f'Bill<{self.bid}> covers updated')

    @property
    def created_at(self) -> datetime:
        """
        Property initiation for the created_at datetime
        """
        return datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S')

    @property
    def created_by_staff_id(self) -> int:
        """
        Property initiation for the created_by_staff_id
        """
        return self._created_by_staff_id

    @created_by_staff_id.setter
    def created_by_staff_id(self, new_sid: int) -> None:
        """
        Updates the created_by_staff_id of the Bill by ID
        """
        # If new_sid is not an int, raise a TypeError
        validate_types([(new_sid, int, 'new_sid')])

        # TODO If new_sid is not an existing staff, raise a ValueError
        # if not row_exists('staff', new_sid):
        #     raise ValueError(f'Staff<{new_sid}> does not exist')

        # If new_sid is valid, update the created_by_staff_id
        self.cur.execute(f"""
            UPDATE bill 
            SET 
                created_by_staff_id = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_sid, datetime.now(), self.bid))
        self.db.commit()

        self._created_by_staff_id = new_sid
        print(f'Bill<{self.bid}> created_by_staff_id updated')

    @property
    def created_by_staff(self) -> None:  # | Staff
        """
        Property initiation for the created_by_staff
        """
        return self._created_by_staff

    @created_by_staff.getter
    def created_by_staff(self) -> None:  # | Staff
        """
        Getter for the created_by_staff
        """
        pass

    @created_by_staff.setter
    def created_by_staff(self, new_sid) -> None:
        """
        Setter for the created_by_staff
        """
        pass

    @property
    def updated_at(self) -> datetime:
        """
        Property initiation for the updated_at datetime
        """
        return  datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S')

    @updated_at.setter
    def updated_at(self, new_updated_at: datetime) -> None:
        """
        Updates the updated_at of the Bill by ID
        """

        # Validate types
        validate_types([(new_updated_at, datetime, 'new_updated_at')])

        # If new_updated_at is in the future, raise a ValueError
        if new_updated_at > datetime.now():
            raise ValueError(f'Updated at must be in the past, not {new_updated_at}')

        # If new_updated_at is valid, update the updated_at
        self.cur.execute(f"""
            UPDATE bill 
            SET 
                updated_at = ?
            WHERE id = ?
        """, (new_updated_at, self.bid))
        self.db.commit()

        self._updated_at = new_updated_at
        print(f'Bill<{self.bid}> updated_at updated')

    def __repr__(self) -> str:
        """
        Representation of the Bill class
        """
        return f'<Bill id={self.bid}, customer_id={self.customer_id}, seating_id={self.seating_id}, total={self.total}, covers={self.covers}, created_at={self.created_at}, created_by_staff_id={self.created_by_staff_id}, updated_at={self.updated_at}>'

    def __eq__(self, other):
        """
        Equality check for the Bill class
        """
        return (
                self.bid == other.bid
                and self.customer_id == other.customer_id
                and self.seating_id == other.seating_id
                and self.total == other.total
                and self.covers == other.covers
                and self.created_at == other.created_at
                and self.created_by_staff_id == other.created_by_staff_id
                and self.updated_at == other.updated_at
        )


class Bills:
    """
    Bills class for the bills table
    """

    def __init__(self, cur: Cursor, db: Connection) -> None:
        """
        Constructor for the Bills class
        """
        # If cur or db is None, raise a TypeError
        if cur is None or db is None:
            raise TypeError(f'Cursor and database cannot be None')

        validate_types([(cur, Cursor, 'cur'), (db, Connection, 'db')])

        # If cur is not connected to db, raise a ValueError
        if cur.connection is not db:
            raise ValueError(f'Cursor is not connected to database')

        # If cur & db are both valid, set them
        self.cur = cur
        self.db = db


        # If the bills table does not exist, create it
        if not table_exists('bills'):
            self.__create_table()

        # If the bills table is empty, set to an empty list
        try:
            self._bills = [Bill(bid[0], self.cur, self.db) for bid in self.cur.execute("SELECT id FROM bill").fetchall()]
        except OperationalError:
            self._bills = []

    @property
    def bills(self) -> list:
        """
        Property initiation for the bills
        """
        return self._bills

    @bills.getter
    def bills(self) -> list:
        """
        Getter for the bills
        """
        return [Bill(bid[0], self.cur, self.db) for bid in self.cur.execute(f"""
                SELECT id FROM bill
            """).fetchall()] or []

    @bills.setter
    def bills(self, new_bills: list) -> None:
        """
        Setter for the bills
        """
        self._bills = new_bills

    def __create_table(self):
        """
        Creates the bills table
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bill (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                seating_id INTEGER,
                total FLOAT DEFAULT 0.0,
                covers INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_staff_id INTEGER,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer (id),
                FOREIGN KEY (seating_id) REFERENCES seating (id),
                FOREIGN KEY (created_by_staff_id) REFERENCES staff (id)
            )
        """)
        self.db.commit()
        print('Bills table created')

    def __drop_table(self):
        """
        Drops the bills table
        """
        self.cur.execute("""
            DROP TABLE IF EXISTS bill
        """)
        self.db.commit()
        print('Bills table dropped')

    def add(self, customer_id: int = None, seating_id: int = None, created_by_staff_id: int = None, total: float = 0.0,
            covers: int = 0) -> Bill:
        """
        Adds a bill to the bills table
        :return:
        """

        types_to_valid = []

        # Change None values to NULL for SQL
        if customer_id is None:
            customer_id = 'NULL'
        else:
            types_to_valid.append((customer_id, int, 'customer_id'))

        if seating_id is None:
            seating_id = 'NULL'
        else:
            types_to_valid.append((seating_id, int, 'seating_id'))

        if created_by_staff_id is None:
            created_by_staff_id = 'NULL'
        else:
            types_to_valid.append((created_by_staff_id, int, 'created_by_staff_id'))

        # Valid all inputs
        validate_types(types_to_valid)

        # If total is negative, raise a ValueError
        if total < 0:
            raise ValueError(f'Total must be positive, not {total}')

        if not get_customer(cid=customer_id, cur=self.cur, db=self.db):
            raise ValueError(f'Customer<{customer_id}> does not exist')
        # if not self.seatings.get(sid=seating_id):
        #     raise ValueError(f'Seating<{seating_id}> does not exist')
        # if not self.staff.get(sid=created_by_staff_id):
        #     raise ValueError(f'Staff<{created_by_staff_id}> does not exist')

        new_bill_id = self.cur.execute(f"""
                INSERT INTO bill (customer_id, seating_id, total, covers, created_by_staff_id) VALUES (?, ?, ?, ?, ?)
            """, (customer_id, seating_id, total, covers, created_by_staff_id)).lastrowid
        self.db.commit()
        new_bill = Bill(
            new_bill_id,
            self.cur,
            self.db
        )

        return new_bill

    def delete(self, bid):
        """
        Deletes a bill from the bills table
        """
        if not [bill for bill in self.bills if bill.bid == bid] or not row_exists('bill', bid):
            raise ValueError(f'Bill<{bid}> does not exist')

        bill_to_delete = self.get(bid=bid)

        self.cur.execute(f"""
            DELETE FROM bill WHERE id = {bid}
        """)

        self.db.commit()

        self.bills = [bill for bill in self.bills if bill.bid != bid]
        print(f'Bill<{bid}> deleted')

        return bill_to_delete

    def get(self, **kwargs):
        if not kwargs:
            return self.bills

        # Extract kwargs
        key, value = next(iter(kwargs.items()))
        if key == 'created_between' or key == 'updated_between':
            start, end = value
            validate_types([(start, datetime, 'start'), (end, datetime, 'end')])
            return [bill for bill in self.bills if start <= getattr(bill, f'{key.split('_')[0]}_at') <= end]
        else:
            return [bill for bill in self.bills if getattr(bill, key) == value]

    def __repr__(self):
        return f'<Bills {self.bills[0:5]}...>'
