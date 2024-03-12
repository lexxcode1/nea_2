from sqlite3 import Cursor, Connection

from .base import RowBase, TableBase



class Role(RowBase):

    table_name = 'role'
    attributes = ['name']
    def __init(self, rid: int, cur: Cursor, db: Connection):
        from helper import validate_types

        self.validate_types = validate_types

        # Get all the attributes of the Role
        super().__init__(rid, cur, db)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        # Validate types
        self.validate_types([(new_name, str, 'new_name')])

        # If new_name is not between 1 and 25 characters long, raise ValueError
        if len(new_name) < 1 or len(new_name) > 25:
            raise ValueError('new_name must be between 1 and 25 characters long')

        # Set the name
        self.set_attribute('name', new_name)

class Roles(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS role (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.db.commit()
        print('Roles table created')

    def __init__(self, cur: Cursor, db: Connection):
        super().__init__(cur, db, 'role', Role)

        self.add_initial_roles()

    def add_initial_roles(self):
        roles = ['server', 'bartender', 'supervisor', 'manager', 'superuser']

        for role in roles:
            if not self.get(name=role):
                self.add(role)

    def add(self, name: str) -> Role:
        # Validate types
        self.validate_types([(name, str, 'name')])

        # If name is not between 1 and 25 characters long, raise ValueError
        if len(name) < 1 or len(name) > 25:
            raise ValueError('name must be between 1 and 25 characters long')

        # Add the role
        new_role = Role(row_id=self.cur.execute('''
            INSERT INTO role (name)
            VALUES (?)
        ''', (name,)).lastrowid, cur=self.cur, db=self.db)

        self.db.commit()
        print(f'Role<{name}> added')

        return new_role

