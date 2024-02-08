from abc import abstractmethod, ABC
from datetime import datetime
from sqlite3 import Cursor, Connection

from helper import validate_types, row_exists, table_exists


class RowBase:
    """
    Base class for all rows in the database

    Attributes
    ----------
    cur : Cursor
        Cursor to the database
    db : Connection
        Connection to the database
    __table_name : str
        Name of the table in the database
    _id : int
        ID of the row in the table
    _attributes : list
        List of columns in the table

    Methods
    -------
    set_attribute(attribute: str, new_value: any) -> None
        Set the value of an attribute in the row

    :returns None
    """

    def __init__(self, rid: int, cur: Cursor, db: Connection, table_name: str, attributes: list[str]) -> None:
        """
        Initialise the RowBase class, setting the cursor and db, and setting the attributes of the row

        :param rid: int ID of the row in the table
        :param cur: Cursor Cursor to the database
        :param db: Connection Connection to the database
        :param table_name: str Name of the table in the database
        :param attributes: list[str] List of columns in the table

        :returns None
        """
        # Validate types
        validate_types(
            [(rid, int, 'rid'), (cur, Cursor, 'cur'), (db, Connection, 'db'), (table_name, str, 'table_name'),
             (attributes, list, 'attributes')])

        # Check if the table exists
        if not table_exists(table_name):
            raise ValueError(f'Table {table_name} does not exist')

        # Remove id, created_at, updated_at from attributes if they are present
        check = ['id', 'created_at', 'updated_at']
        attributes = [attribute for attribute in attributes if attribute not in check]

        # Check if the cursor is connected to the db
        if cur.connection is not db:
            raise ValueError('Cursor is not connected to the database')

        # Set the cursor and db
        self.cur = cur
        self.db = db

        # Check if the row exists
        if not row_exists(table_name, rid):
            raise ValueError(f'{self.__class__.__name__}<{rid}> does not exist')

        # Set the table name and attributes
        self.__table_name = table_name
        attributes = ['id', *attributes, 'created_at', 'updated_at']

        # Set up attributes
        query = f'SELECT {", ".join(attributes)} FROM {table_name} WHERE id = ?'
        try:
            self._id, *self._attributes = self.cur.execute(query, (rid,)).fetchone()
        except TypeError:
            raise ValueError(f'{self.__class__.__name__}<{rid}> does not exist')

        # set attributes
        for i, attribute in enumerate(attributes[1:]):
            try:
                setattr(self, f'_{attribute}', self._attributes[i])
            except AttributeError as e:
                if 'has no setter' in str(e):
                    print(f'{attribute} has no setter')
                    continue
                raise e

    def set_attribute(self, attribute: str, new_value: any) -> None:
        """
        Set the value of an attribute in the row

        :param attribute: str Name of the attribute to set
        :param new_value: any New value to set the attribute to
        """
        # Validate types
        validate_types([(attribute, str, attribute)])

        # Check if the attribute exists
        if not hasattr(self, f'{attribute}'):
            raise ValueError(f'{self.__class__.__name__}<{self._id}> does not have attribute {attribute}')

        # Check if the new value is the same as the current value
        if new_value == getattr(self, f'{attribute}'):
            print(f'{self.__class__.__name__}<{self._id}> {attribute} is already {new_value}')
            return

        print((datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
        # Update the attribute
        query = f'''
            UPDATE {self.__table_name}
            SET 
                {attribute} = ?,
                updated_at = ?
            WHERE id = ?
        '''
        self.cur.execute(query, (new_value, datetime.now(), self._id))
        self.db.commit()

        # Update the attribute in the object
        setattr(self, f'_{attribute}', new_value if new_value is not None else None) \
            if hasattr(self, f'_{attribute}') else setattr(self, attribute, new_value)

        # Update the updated_at attribute
        self._updated_at = datetime.now()

        print(f'{self.__class__.__name__}<{self._id}> {attribute} updated')

        return new_value

    @property
    def created_at(self) -> datetime:
        """
        Property initiation for the created_at datetime
        """
        return datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S') if type(
            self._created_at) is str else self._created_at

    @created_at.setter
    def created_at(self, new_created_at: datetime | str) -> None:
        """
        Updates the created_at of the Bill by ID
        """
        new_created_at = new_created_at[0: new_created_at.rfind('.')]
        if type(new_created_at) is str:
            new_created_at = datetime.strptime(new_created_at, '%Y-%m-%d %H:%M:%S')
        # Validate types
        validate_types([(new_created_at, datetime, 'new_created_at')])

        # If new_created_at is in the future, raise a ValueError
        if new_created_at > datetime.now():
            raise ValueError(f'Created at must be in the past, not {new_created_at}')

        self.set_attribute('created_at', new_created_at)

    @property
    def updated_at(self) -> datetime:
        """
        Property initiation for the updated_at datetime
        """
        return self._updated_at if type(
            self._updated_at
        ) is not str else datetime.strptime(self._updated_at, '%Y-%m-%d %H:%M:%S')

    # I dont think this is needed because it is always updated anyway
    @updated_at.setter
    def updated_at(self, new_updated_at: datetime | str) -> None:
        """
        Updates the updated_at of the Bill by ID
        """
        new_updated_at = new_updated_at[0: new_updated_at.rfind('.')]
        if type(new_updated_at) is str:
            new_updated_at = datetime.strptime(new_updated_at, '%Y-%m-%d %H:%M:%S')
        # Validate types
        validate_types([(new_updated_at, datetime, 'new_updated_at')])

        # If new_updated_at is in the future, raise a ValueError
        if new_updated_at > datetime.now():
            raise ValueError(f'Updated at must be in the past, not {new_updated_at}')

        self.set_attribute('updated_at', new_updated_at)


class TableBase(ABC):
    def __init__(self, cur: Cursor, db: Connection, table_name: str, RowClass: any, rid_attr_name: str) -> None:
        # Validate types of cur and db
        validate_types([(cur, Cursor, 'cur'), (db, Connection, 'db'), (table_name, str, 'table_name'),
                        (rid_attr_name, str, 'rid_attr_name')])

        # Check that Child is a subclass of RowBase
        if not issubclass(RowClass, RowBase):
            raise TypeError('Child must be a subclass of RowBase')

        self.RowClass = RowClass

        # Check if the rid_attr_name is a valid attribute
        if rid_attr_name not in [attr for attr in dir(self.RowClass) if
                                 not callable(getattr(self.RowClass, attr))]:
            raise ValueError(f'{rid_attr_name} is not a valid attribute of {self.RowClass.__class__.__name__}')

        # Set the rid_attr_name
        self.__rid_attr_name = rid_attr_name

        # Check the cursor is connected to the database
        if not cur.connection:
            raise ConnectionError('Cursor is not connected to the database')

        # Set the cursor and database
        self.cur = cur
        self.db = db

        # Set the table name
        self.table_name = table_name

        # Check if the table exists
        if not table_exists(table_name):
            self.create_table()

        self._rows = [RowClass(x[0], self.cur, self.db) for x in
                      self.cur.execute(f'SELECT id FROM {table_name}').fetchall()]

    @property
    def rows(self) -> list[RowBase]:
        return self._rows

    @rows.getter
    def rows(self) -> list[RowBase]:
        return [self.RowClass(x[0], self.cur, self.db) for x in
                self.cur.execute(f'SELECT id FROM {self.table_name}').fetchall()]

    @rows.setter
    def rows(self, new_items: list[RowBase]) -> None:
        self._rows = new_items

    def __handle_between_dates(self, key, value):
        start, end = value
        validate_types([(start, datetime, 'start'), (end, datetime, 'end')])

        # If the end is before the start, raise a ValueError
        if start > end:
            raise ValueError('Start date must be before end date')

        return [row for row in self.rows if start <= getattr(row, f'{key.split('_')[0]}_at') <= end]

    @staticmethod
    def __handle_valid_matches(match_all, valid_matches, new_matches):
        if match_all:
            valid_matches = new_matches if not valid_matches else [row for row in valid_matches if
                                                                   row in new_matches]
        else:
            valid_matches = new_matches if not valid_matches else valid_matches + new_matches
        return valid_matches

    def get(self, match_all: bool = False, **kwargs):

        valid_matches = []
        for key, value in kwargs.items():
            between_dates = key == 'created_between' or key == 'updated_between'

            new_matches = [row for row in self.rows if
                           getattr(row, key) == value] if not between_dates else self.__handle_between_dates(key, value)
            valid_matches = self.__handle_valid_matches(match_all, valid_matches, new_matches)
        return valid_matches

    def clear(self):
        self.cur.execute(f"DELETE FROM {self.table_name}")
        self.db.commit()
        self._rows = []

    def count(self):
        return self.cur.execute(f"SELECT COUNT(*) FROM {self.table_name}").fetchone()[0]

    def delete(self, rid) -> None:
        """
       Delete a row from the table
       :return:
       """
        # Validate types
        validate_types([(rid, int, 'rid')])

        # If the seat does not exist, raise an error
        if not self.cur.execute(f"SELECT * FROM {self.table_name} WHERE id = {rid}").fetchone():
            raise ValueError(f"{self.RowClass.__class__.__name__}<{rid}> does not exist")

        # Delete the Seat from the database
        self.cur.execute(f"DELETE FROM {self.table_name} WHERE id = {rid}")
        self.db.commit()

        # Update the rows
        self.rows = [row for row in self.rows if getattr(row, self.__rid_attr_name) != rid]

    def drop_table(self):
        self.cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        self.db.commit()
        self._rows = []

    @abstractmethod
    def add(self, **kwargs) -> None:
        pass

    @abstractmethod
    def create_table(self) -> None:
        pass
