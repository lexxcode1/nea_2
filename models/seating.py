from datetime import datetime, timedelta
from sqlite3 import Cursor, Connection

from helper import validate_types, table_exists


class Seat:
    def __init__(self, sid: int, cur: Cursor, db: Connection) -> None:
        self.cur = cur
        self.db = db
        self._id = sid
        attributes = ['name', 'max_size', 'flagged', 'status', 'type', 'created_at', 'updated_at']
        query = f"SELECT {', '.join(attributes)} FROM seating WHERE id = {self._id}"
        (self._name, self._max_size, self._flagged, self._status, self._type, self._created_at,
         self._updated_at) = self.cur.execute(query).fetchone()

    @property
    def id(self) -> int:
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

        # Update the database
        self.cur.execute(f"UPDATE seating SET name = '{new_name}' WHERE id = {self._id}")
        self.db.commit()
        self._name = new_name

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

        # If new_max_size is the same as the current max_size, return
        if new_max_size == self._max_size:
            return

        # If new_max_size is less than 1, raise ValueError
        if new_max_size < 0:
            raise ValueError('new_max_size must be greater than 0')

        # Update the database
        self.cur.execute(f"UPDATE seating SET max_size = {new_max_size} WHERE id = {self._id}")
        self.db.commit()
        self._max_size = new_max_size

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

        # If new_flagged is the same as the current flagged, return
        if new_flagged == self._flagged:
            return

        # Update the database
        self.cur.execute(f"UPDATE seating SET flagged = {new_flagged} WHERE id = {self._id}")
        self.db.commit()
        self._flagged = new_flagged

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

        # If new_status is the same as the current status, return
        if new_status == self._status:
            return

        # Update the database
        self.cur.execute(f"UPDATE seating SET status = '{new_status}' WHERE id = {self._id}")
        self.db.commit()
        self._status = new_status

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

        # If new_type is the same as the current type, return
        if new_type == self._type:
            return

        # Update the database
        self.cur.execute(f"UPDATE seating SET type = '{new_type}' WHERE id = {self._id}")
        self.db.commit()
        self._type = new_type

    @property
    def created_at(self) -> datetime:
        """
        Get the created_at of the Seat

        :return str : created_at of the Seat
        """
        return datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S')

    @property
    def updated_at(self) -> datetime:
        """
        Get the updated_at of the Seat

        :return str : updated_at of the Seat
        """
        return datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S')

    @updated_at.setter
    def updated_at(self, new_updated_at: datetime) -> None:
        """
        Set the updated_at of the Seat
        :param new_updated_at:
        :return:
        """
        # Validate types
        validate_types([(new_updated_at, datetime, 'new_updated_at')])

        # If new_updated_at is in the future, raise ValueError
        if new_updated_at > datetime.now():
            raise ValueError('new_updated_at cannot be in the future')

        # If new_updated_at is over one day in the past, raise ValueError
        if new_updated_at < datetime.now() - timedelta(days=1):
            raise ValueError('new_updated_at cannot be over one day in the past')

        # If new_updated_at is the same as the current updated_at, return
        if new_updated_at == self._updated_at:
            return

        # Update the database
        self.cur.execute(f"UPDATE seating SET updated_at = '{new_updated_at}' WHERE id = {self._id}")
        self.db.commit()
        self._updated_at = new_updated_at

    @property
    def bills(self) -> list:
        """
        Get the bills of the Seat

        :return list : bills of the Seat
        """
        return self.cur.execute(f"SELECT id FROM bill WHERE table_id = {self._id}").fetchall()

    @bills.getter
    def bills(self) -> list:
        """
        Get the bills of the Seat

        :return list : bills of the Seat
        """
        return self.cur.execute(f"SELECT id FROM bill WHERE table_id = {self._id}").fetchall()

    @property
    def current_occupancy(self):
        """
        Get the current occupancy of the Seat

        :return int : current occupancy of the Seat
        """
        return self.cur.execute(f"SELECT COUNT(covers) FROM bill WHERE table_id = {self._id}").fetchone()[0]

    @property
    def is_full(self):
        """
        Get the is_full of the Seat

        :return bool : is_full of the Seat
        """
        return self.current_occupancy >= self._max_size

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


class Seating:
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

        # Validate types of cur and db
        validate_types([(cur, Cursor, 'cur'), (db, Connection, 'db')])

        # Check the cursor is connected to the database
        if not cur.connection:
            raise ConnectionError('Cursor is not connected to the database')

        # Set the cursor and database
        self.cur = cur
        self.db = db

        # Check if the table exists
        if not table_exists('seating'):
            self.__create_table()

        self._seats = [Seat(x[0]) for x in self.cur.execute('SELECT id FROM seating').fetchall()]

    @property
    def seats(self) -> list[Seat]:
        """
        Get a list of Seats from the database

        :return list[Seat] : list of Seats from the database
        """
        return self._seats

    @seats.getter
    def seats(self) -> list[Seat]:
        """
        Get a list of Seats from the database

        :return list[Seat] : list of Seats from the database
        """
        return [Seat(x[0]) for x in self.cur.execute('SELECT id FROM seating').fetchall()]

    @seats.setter
    def seats(self, new_seats: list[Seat]) -> None:
        """
        Set the list of Seats in the database

        :param new_seats: list[Seat] New list of Seats
        :return None:
        """
        self._seats = new_seats

    def get(self, **kwargs) -> list[Seat]:
        """
        Get a list of Seats from the database

        :param kwargs: dict of attributes to search by
        :return list[Seat] : list of Seats from the database
        """

        key, value = next(iter(kwargs.items()))
        return [seat for seat in self.seats if getattr(seat, key) == value]

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

        # Add the new Seat to the list of Seats
        self.seats.append(new_seat)

        return new_seat

    def delete(self, sid: int):
        """
        Delete a Seat from the database
        :return:
        """
        # Validate types
        validate_types([(sid, int, 'sid')])

        # If the seat does not exist, raise an error
        if not self.cur.execute(f"SELECT * FROM seating WHERE id = {sid}").fetchone():
            raise ValueError(f"Seat<{sid}> does not exist")

        # Delete the Seat from the database
        self.cur.execute(f"DELETE FROM seating WHERE id = {sid}")
        self.db.commit()
        self.seats = [seat for seat in self.seats if seat.id != sid]

    def __repr__(self):
        return '<Seating>'
