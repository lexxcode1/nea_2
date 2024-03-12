from abc import abstractmethod, ABC
from datetime import datetime
from sqlite3 import Cursor, Connection

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

    def __init__(self, row_id: int, cur: Cursor, db: Connection) -> None:
        """
        Initialise the RowBase class, setting the cursor and db, and setting the attributes of the row

        :param row_id: int ID of the row in the table
        :param cur: Cursor Cursor to the database
        :param db: Connection Connection to the database

        :returns None
        """
        from helper import table_exists, row_exists

        # Validate types
        self.validate_types(
            [(row_id, int, 'row_id'), (cur, Cursor, 'cur'), (db, Connection, 'db'),
             (self.table_name, str, 'table_name'),
             (self.attributes, list, 'attributes')])

        # Check if the table exists
        if not table_exists(self.table_name):
            raise ValueError(f'Table {self.table_name} does not exist')

        # Remove id, created_at, updated_at from attributes if they are present
        check = ['id', 'created_at', 'updated_at']
        self.attributes = [attribute for attribute in self.attributes if attribute not in check]

        # Check if the cursor is connected to the db
        if cur.connection is not db:
            raise ValueError('Cursor is not connected to the database')

        # Set the cursor and db
        self.cur = cur
        self.db = db

        # Check if the row exists
        if not row_exists(self.table_name, row_id):
            raise ValueError(f'{self.__class__.__name__}<{row_id}> does not exist')

        # Set the table name and attributes
        self.attributes = ['id', *self.attributes, 'created_at', 'updated_at']

        # Set up attributes
        query = f'SELECT {", ".join(self.attributes)} FROM {self.table_name} WHERE id = ?'

        try:
            self._id, *self._attributes = self.cur.execute(query, (row_id,)).fetchone()
        except TypeError:
            raise ValueError(f'{self.__class__.__name__}<{row_id}> does not exist')

        # set attributes
        for i, attribute in enumerate(self.attributes[1:]):
            try:
                setattr(self, f'_{attribute}', self._attributes[i])
            except AttributeError as e:
                if 'has no setter' in str(e):
                    print(f'{attribute} has no setter')
                    continue
                raise e

    def validate_types(self, types):
        from helper import validate_types
        validate_types(types)

    def row_exists(self, table_name, row_id):
        from helper import row_exists
        return row_exists(table_name, row_id)

    def set_attribute(self, attribute: str, new_value: any) -> None:
        """
        Set the value of an attribute in the row

        :param attribute: str Name of the attribute to set
        :param new_value: any New value to set the attribute to
        """
        # Validate types
        self.validate_types([(attribute, str, attribute)])

        # Check if the attribute exists
        if not hasattr(self, f'{attribute}'):
            raise ValueError(f'{self.__class__.__name__}<{self._id}> does not have attribute {attribute}')

        # Check if the new value is the same as the current value
        if new_value == getattr(self, f'{attribute}'):
            print(f'{self.__class__.__name__}<{self._id}> {attribute} is already {new_value}')
            return

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
        self.validate_types([(new_created_at, datetime, 'new_created_at')])

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
        self.validate_types([(new_updated_at, datetime, 'new_updated_at')])

        # If new_updated_at is in the future, raise a ValueError
        if new_updated_at > datetime.now():
            raise ValueError(f'Updated at must be in the past, not {new_updated_at}')

        self.set_attribute('updated_at', new_updated_at)

    def __hash__(self):
        return hash(self._id)

    def __del__(self):
        self.cur.execute(f"DELETE FROM {self.table_name} WHERE id = {self._id}")


class TableBase(ABC):
    def __init__(self, cur: Cursor, db: Connection, table_name: str, RowClass: any, rid_attr_name: str = 'id') -> None:
        # Validate types of cur and db
        from helper import table_exists
        self.validate_types([(cur, Cursor, 'cur'), (db, Connection, 'db'), (table_name, str, 'table_name'),
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

    def validate_types(self, types):
        from helper import validate_types
        validate_types(types)


    def row_exists(self, table_name, row_id):
        from helper import row_exists
        return row_exists(table_name, row_id)

    @property
    def rows(self) -> list[RowBase]:
        return self._rows

    @rows.getter
    def rows(self) -> list[RowBase]:
        return [self.RowClass(x[0], self.cur, self.db) for x in
                self.cur.execute(f'SELECT id FROM {self.table_name}').fetchall()]

    @rows.setter
    def rows(self, new_items: list) -> None:
        self._rows = new_items

    def __handle_between_dates(self, key, value):
        start, end = value
        self.validate_types([(start, datetime, 'start'), (end, datetime, 'end')])

        # If the end is before the start, raise a ValueError
        if start > end:
            raise ValueError('Start date must be before end date')

        return [row for row in self.rows if start <= getattr(row, f'{key.split('_')[0]}') <= end]



    def get(self, match_all: bool = False, **kwargs):
        """
        Get a row from the table by the attributes
        :param match_all: bool, whether to find the intersection (True) or union (False: default)
        :param kwargs: the value to search for (name='John') for example
                If kwargs contains a key that ends with '_between', the value should be a tuple of two values,
                it will check if the value is between the two values in format (start, end)
        :return list[RowClass]: list of rows that match the search
        """
        from helper import walking_binary_search

        # If there are no kwargs, return all the rows
        if not kwargs:
            return self.rows

        # Initialise the final matches set
        final_matches = set()

        # Set ran through to default as False
        ran_through = False

        # Set up a fake rows variable for sorting
        temp_rows = self.rows

        # Loop through items in kwargs
        for key, value in kwargs.items():
            # Check if the key is 'created_between' etc
            between_dates = key.endswith('_between')

            # Sort by the key
            temp_rows.sort(key=lambda x: getattr(x, key))

            # If between_dates is True, handle the between dates
            if between_dates:
                new_matches = self.__handle_between_dates(key, value)
            else:
                # Get all matching values using a walking binary search. See document for flowchart
                new_matches = walking_binary_search(temp_rows, key, value)

                if match_all:
                    # If you have searched temp_rows and found nothing on the first iteration, return an empty list
                    if not final_matches and ran_through:
                        return []

                    # If you have not ran through the loop, set the final matches to the new matches
                    # Otherwise, set the final matches to the intersection of the final matches and the new matches
                    # Set notation: final_matches = final_matches ∩ new_matches
                    final_matches = final_matches & set(new_matches) if ran_through else set(new_matches)

                    # Set the temp_rows to the final_matches to limit the search space
                    temp_rows = list(final_matches)

                    # Set ran_through to True
                    ran_through = True
                else:
                    # Set final_matches to the union of the final matches and the new matches
                    # Set notation: final_matches = final_matches ∪ new_matches
                    final_matches |= set(new_matches)

        # Return the final matches as a list
        return list(final_matches)

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
        self.validate_types([(rid, int, 'rid')])

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
