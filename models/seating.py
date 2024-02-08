from datetime import datetime
from sqlite3 import Cursor, Connection

from facades.bill_only import get_all_bills_by_seat
from helper import validate_types
from models.base import RowBase, TableBase


class Seat(RowBase):
    """
    Seat class for the Seating table in the database
    """

    def __init__(self, sid: int, cur: Cursor, db: Connection) -> None:
        self._bills = []

        # Get all the attributes of the Seat
        attributes = ['name', 'max_size', 'flagged', 'status', 'type']

        super().__init__(sid, cur, db, 'seating', attributes)

    @property
    def sid(self) -> int:
        """
        Get the id of the Seat

        :return int : id of the Seat
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the name of the Seat

        :return str : name of the Seat
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Set the name of the Seat

        :param new_name: str New name of the Seat
        :return None:
        """
        # Validate types
        validate_types([(new_name, str, 'new_name')])

        # If new_name is the same as the current name, return
        if new_name == self._name:
            return

        # If new_name is shorter than 1 character, raise ValueError
        if len(new_name) < 1 or len(new_name) > 25:
            raise ValueError('new_name must be between 1 and 25 characters long')

        self.set_attribute('name', new_name)

    @property
    def max_size(self) -> int:
        """
        Get the max_size of the Seat

        :return int : max_size of the Seat
        """
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size: int) -> None:
        """
        Set the max_size of the Seat

        :param new_max_size: int New max_size of the Seat
        :return None:
        """
        # Validate types
        validate_types([(new_max_size, int, 'new_max_size')])

        # If new_max_size is less than 1, raise ValueError
        if new_max_size < 0:
            raise ValueError('new_max_size must be greater than 0')

        self.set_attribute('max_size', new_max_size)

    @property
    def flagged(self) -> bool:
        """
        Get the flagged of the Seat

        :return bool : flagged of the Seat
        """
        return self._flagged

    @flagged.setter
    def flagged(self, new_flagged: bool) -> None:
        """
        Set the flagged of the Seat

        :param new_flagged: bool New flagged of the Seat
        :return None:
        """
        # Validate types
        validate_types([(new_flagged, bool, 'new_flagged')])

        self.set_attribute('flagged', new_flagged)

    @property
    def status(self) -> str:
        """
        Get the status of the Seat

        :return str : status of the Seat
        """
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        """
        Set the status of the Seat
        :param new_status:
        :return:
        """
        # Validate types
        validate_types([(new_status, str, 'new_status')])

        if new_status not in ['clear', 'reserved', 'okay', 'mains', 'desserts', 'bill', 'paid', 'check']:
            raise ValueError('new_status must be one of clear, reserved, okay, mains, desserts, bill, paid, check')

        self.set_attribute('status', new_status)

    @property
    def type(self) -> str:
        """
        Get the type of the Seat

        :return str : type of the Seat
        """
        return self._type

    @type.setter
    def type(self, new_type: str) -> None:
        """
        Set the type of the Seat
        :param new_type:
        :return:
        """
        # Validate types
        validate_types([(new_type, str, 'new_type')])

        if new_type not in ['table', 'booth', 'bar', 'high-table']:
            raise ValueError('new_type must be one of table, booth, bar, high-table')

        self.set_attribute('type', new_type)

    @property
    def bills(self) -> list:
        """
        Get the bills of the Seat

        :return list : bills of the Seat
        """
        return get_all_bills_by_seat(self.sid, self.cur, self.db)

    @bills.getter
    def bills(self) -> list:
        """
        Get the bills of the Seat

        :return list : bills of the Seat
        """
        self._bills = get_all_bills_by_seat(self.sid, self.cur, self.db)
        return self._bills

    @property
    def current_occupancy(self):
        """
        Get the current occupancy of the Seat

        :return int : current occupancy of the Seat
        """
        return self.cur.execute(f"SELECT COUNT(covers) FROM bill WHERE table_id = {self._id}").fetchone()[0]

    @current_occupancy.getter
    def current_occupancy(self):
        """
        Get the current occupancy of the Seat

        :return int : current occupancy of the Seat
        """
        return self.cur.execute(f"SELECT COUNT(covers) FROM bill WHERE table_id = {self._id}").fetchone()[0]

    def is_full(self):
        """
        Get the is_full of the Seat

        :return bool : is_full of the Seat
        """
        return self.current_occupancy >= self._max_size

    def add_bill(self, bill):
        pass

    def __repr__(self):
        return f'<Seat id={self._id}, name="{self._name}", max_size={self._max_size}, flagged={self._flagged}, ' \
               f'status="{self._status}", type="{self._type}", created_at={self._created_at}, ' \
               f'updated_at={self._updated_at}>'

    def __eq__(self, other):
        return (
                self._id == other._id
                and self._name == other._name
                and self._max_size == other._max_size
                and self._flagged == other._flagged
                and self._status == other._status
                and self._type == other._type
                and self._created_at == other._created_at
                and self._updated_at == other._updated_at
        )


class Seats(TableBase):
    def __create_table(self):
        # Create the table
        self.cur.execute('''
            CREATE TABLE seating (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(25),
                max_size INTEGER DEFAULT 0,
                flagged BOOLEAN DEFAULT FALSE,
                status VARCHAR(155),
                type VARCHAR(155),
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(id) REFERENCES bill (table_id)
            );
        ''')

    def __init__(self, cur: Cursor, db: Connection):
        super().__init__(cur, db, 'seating', Seat, 'sid')

    def add(self, name: str, max_size: int, flagged: bool, status: str, seat_type: str) -> Seat:
        """
        Create a new Seat in the database

        :param name: str Name of the Seat
        :param max_size: int Maximum size of the Seat
        :param flagged: bool True if the Seat is flagged, False otherwise
        :param status: str Status of the Seat
        :param seat_type: str Type of the Seat
        :return Seat : New Seat object
        """

        # Validate types
        validate_types([(name, str, 'name'), (max_size, int, 'max_size'), (flagged, bool, 'flagged'),
                        (status, str, 'status'), (seat_type, str, 'type_')])

        # If name is less than 1 character, raise ValueError
        if len(name) < 1 or len(name) > 25:
            raise ValueError('name must be between 1 and 25 characters long')

        # If max_size is less than 1, raise ValueError
        if max_size < 0:
            raise ValueError('max_size must be greater than or equal to 0')

        if status not in ['clear', 'reserved', 'okay', 'mains', 'desserts', 'bill', 'paid', 'check']:
            raise ValueError('status must be one of clear, reserved, okay, mains, desserts, bill, paid, check')

        if seat_type not in ['table', 'booth', 'bar', 'high-table']:
            raise ValueError('type must be one of table, booth, bar, high-table')

        # Insert the new Seat into the database
        new_id = self.cur.execute(f'''
            INSERT INTO seating (name, max_size, flagged, status, type, created_at, updated_at)
            VALUES ('{name}', {max_size}, {flagged}, '{status}', '{seat_type}', '{datetime.now()}', '{datetime.now()}');
        ''').lastrowid
        self.db.commit()

        # Create a new Seat object
        new_seat = Seat(new_id, self.cur, self.db)

        return new_seat

    def __repr__(self):
        return '<Seating>'
