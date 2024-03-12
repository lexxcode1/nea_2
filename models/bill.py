from sqlite3 import Cursor, Connection
from typing import Union, Tuple, List, TYPE_CHECKING

from facades.action_only import add_action
from facades.customer_only import get_customer
from facades.seat_only import get_seat
from models.base import RowBase, TableBase
from models.billitem import BillItems

if TYPE_CHECKING:
    from models import Item


class Bill(RowBase):
    """
    Bill class for rows in the Bills table
    """

    attributes = ['customer_id', 'seating_id', 'total', 'covers', 'created_by_staff_id']
    table_name = 'bill'

    def __init__(self, bid: int, cur: Cursor, db: Connection) -> None:
        """
        Constructor for the Bill class
        
        Only for use in the Bills class
        """
        self.__bill_items = BillItems(self.cur, self.db)

        self.validate_types([(bid, int, 'bid'), (cur, Cursor, 'cur'), (db, Connection, 'db')])

        # Initiate relationship variables
        self._customer = None
        self._seating = None
        self._seating_id = None
        self._created_by_staff = None

        super().__init__(bid, cur, db)

    def set_attribute(self, attribute: str, new_value: any) -> None:
        """
        Set the attribute of the Bill by ID
        """
        super().set_attribute(attribute, new_value)

        # Create a new action
        add_action(self.cur, self.db, bill_id=self.id, staff_id=self.created_by_staff_id, action_type=f'update')

    @property
    def id(self) -> int:
        """
        Property initiation for the id
        """
        return self._id

    @property
    def customer_id(self) -> int | str:
        """
        Property initiation for the customer_id
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, new_cid: int | None | str) -> None:
        """
        Updates the customer_id of the Bill by ID
        """
        # If the customer_id is None, set it to NULL
        if new_cid is None or new_cid == 'NULL':
            new_cid = 'NULL'
            self._customer_id = None
        else:
            self.validate_types([(new_cid, int, 'new_cid')])
            # If the customer_id is not None, check if the customer exists
            if not get_customer(cid=new_cid, cur=self.cur, db=self.db):
                raise ValueError(f'Customer<{new_cid}> does not exist')

        self.set_attribute('customer_id', new_cid)

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
        self._customer = new_customer if new_customer is not None else None

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
        if new_sid is None or new_sid == 'NULL':
            new_sid = 'NULL'
            self._seating_id = None
        else:
            types_to_valid.append((new_sid, int, 'new_sid'))

        # If new_tid is not None or int, raise a TypeError
        self.validate_types(types_to_valid)

        # TODO If new_tid is not an existing table, raise a ValueError

        self.set_attribute('seating_id', new_sid)

    @property
    def seat(self):
        return self._seating

    @seat.getter
    def seat(self):
        try:
            return get_seat(sid=self._seating_id, cur=self.cur, db=self.db)
        except ValueError:
            return None

    @seat.setter
    def seat(self, new_seat):
        if new_seat is None:
            self.seating_id = None
            self._seating = None

        # Try to get the seat, if it does not exist, set the seating_id to None
        try:
            get_seat(sid=new_seat.sid, cur=self.cur, db=self.db)
            self.seating_id = new_seat.sid
            self._seating = new_seat
        except ValueError:
            self.seating_id = None
            self._seating = None

    @property
    def total(self) -> float:
        """
        Property initiation for the total
        """
        # Get all the bill items for the bill and sum the total if complimentary is not in the staff_note

        return sum(
            [item.price for item in self.__bill_items.get(bid=self.id) if 'complimentary' not in item.staff_note])

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

        self.validate_types([(new_covers, int, 'new_covers')])

        # If new_covers is greater than 999 or less than 0, raise a ValueError
        if new_covers > 999 or new_covers < 0:
            raise ValueError(f'Covers must be between 0 and 999, not {new_covers}')

        # If new_covers is valid, update the covers
        self.set_attribute('covers', new_covers)

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
        if new_sid is None or new_sid == 'NULL':
            new_sid = 'NULL'
            self._created_by_staff_id = None
        else:
            self.validate_types([(new_sid, int, 'new_sid')])

        # TODO If new_sid is not an existing staff, raise a ValueError
        # if not self.row_exists('staff', new_sid):
        #     raise ValueError(f'Staff<{new_sid}> does not exist')

        # If new_sid is valid, update the created_by_staff_id
        self.set_attribute('created_by_staff_id', new_sid)

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

    def add_items(self, items: Union['Item', Tuple['Item', str], List[Tuple['Item', str]]] | 'Item', staff_id):
        staff_note = 'NULL'

        if type(items) is 'Item' or tuple['Item', str]:
            items = [items]

        for item in items:
            if type(item) is list[tuple[self.Item, str]]:
                item, staff_note = item
            self.__add_item(item, staff_id, staff_note)

        # Create a new action
        add_action(self.cur, self.db, bill_id=self.id, staff_id=staff_id, action_type='update_bill_items',
                   approved=True, approval_id=None, approved_at=None)

    def __add_item(self, item: 'Item', staff_id: int, staff_note: str = 'NULL'):
        self.__bill_items.add(self.id, item.id, staff_id, staff_note=staff_note)

    def remove_items(self, items: list | tuple, staff_id):
        for item in items:
            # Get the rows from the bill_items table
            rows = self.__bill_items.get(bid=self.id, iid=item.id)[0]

            # If the item is not in the bill, raise a ValueError
            if not rows:
                print(f'Item<{item.id}> is not in the bill')
                continue

            # If the quantity is greater than one and the item is in the bill, remove one from the quantity
            if rows and rows.quantity > 1:
                rows.quantity -= 1
                continue

            # If the quantity is one, remove the item from the bill
            if rows and rows.quantity == 1:
                self.__bill_items.delete(rows.id)

        # Create a new action
        add_action(self.cur, self.db, bill_id=self.id, staff_id=staff_id, action_type='update_bill_items',
                   approved=True, approval_id=None, approved_at=None)

    def __repr__(self) -> str:
        """
        Representation of the Bill class
        """
        return f'<Bill id={self.id}, customer_id={self.customer_id}, seating_id={self.seating_id}, total={self.total}, covers={self.covers}, created_at={self.created_at}, created_by_staff_id={self.created_by_staff_id}, updated_at={self.updated_at}>'

    def __eq__(self, other):
        """
        Equality check for the Bill class
        """
        return (
                self.id == other.id
                and self.customer_id == other.customer_id
                and self.seating_id == other.seating_id
                and self.total == other.total
                and self.covers == other.covers
                and self.created_at == other.created_at
                and self.created_by_staff_id == other.created_by_staff_id
                and self.updated_at == other.updated_at
        )


class Bills(TableBase):
    """
    Bills class for the bills table
    """

    def __init__(self, cur: Cursor, db: Connection) -> None:
        """
        Constructor for the Bills class
        """

        super().__init__(cur, db, 'bill', Bill, )

    def create_table(self):
        """
        Creates the bills table
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bill (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                seating_id INTEGER,
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

    def add(self, customer_id: int = None, seating_id: int = None, created_by_staff_id: int = None, total: float = 0.0,
            covers: int = 0) -> Bill:
        """
        Adds a bill to the bills table
        :return:
        """

        if created_by_staff_id is not None and not self.row_exists('staff', created_by_staff_id):
            raise ValueError(f'Staff<{created_by_staff_id}> does not exist')

        types_to_valid = []

        # Change None values to NULL for SQL
        if customer_id is None or customer_id == 'NULL':
            customer_id = 'NULL'
        else:
            if not get_customer(cid=customer_id, cur=self.cur, db=self.db):
                raise ValueError(f'Customer<{customer_id}> does not exist')

            # Add the customer_id to the types_to_valid list
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
        self.validate_types(types_to_valid)

        # If total is negative, raise a ValueError
        if total < 0:
            raise ValueError(f'Total must be positive, not {total}')

        # If covers is greater than 999 or less than 0, raise a ValueError
        if covers > 999 or covers < 0:
            raise ValueError(f'Covers must be between 0 and 999, not {covers}')

        # if not self.seatings.get(sid=seating_id):
        #     raise ValueError(f'Seating<{seating_id}> does not exist')
        # if not self.staff.get(sid=created_by_staff_id):
        #     raise ValueError(f'Staff<{created_by_staff_id}> does not exist')

        # Add the bill to the bills table
        new_bill_id = self.cur.execute(f"""
                INSERT INTO bill (customer_id, seating_id, covers, created_by_staff_id) VALUES (?, ?, ?, ?)
            """, (customer_id, seating_id, covers, created_by_staff_id)).lastrowid
        self.db.commit()
        new_bill = Bill(
            new_bill_id,
            self.cur,
            self.db
        )

        if created_by_staff_id is not None:
            # Create an action for the bill creation
            add_action(self.cur, self.db, bill_id=new_bill_id, staff_id=created_by_staff_id, action_type='create')

        return new_bill

    def __repr__(self):
        return f'<Bills {self.rows[0:5]}...>'
