from sqlite3 import Cursor, Connection

from .base import RowBase, TableBase


class Approval(RowBase):
    """
    This class represents an Approval in the database
    """

    attributes = ['staff_id', 'shift_id', 'action_id']
    table_name = 'approval'
    def __init__(self, aid: int, cur, db) -> None:
        super().__init__(aid, cur, db)

    @property
    def id(self) -> int:
        return self._id

    @property
    def staff_id(self) -> int:
        return self._staff_id

    @staff_id.setter
    def staff_id(self, new_staff_id: int) -> None:
        # Validate inputs
        self.validate_types([(new_staff_id, int, 'new_staff_id')])

        # If there is no staff with the new_staff_id, raise ValueError
        if not self.row_exists('staff', new_staff_id):
            raise ValueError(f'Staff<{new_staff_id}> does not exist')

        self.set_attribute('staff_id', new_staff_id)

    @property
    def shift_id(self) -> int:
        return self._shift_id

    @shift_id.setter
    def shift_id(self, new_shift_id: int) -> None:
        # Validate inputs
        self.validate_types([(new_shift_id, int, 'new_shift_id')])

        # If there is no shift with the new_shift_id, raise ValueError
        if not self.row_exists('shift', new_shift_id):
            raise ValueError(f'Shift<{new_shift_id}> does not exist')

        self.set_attribute('shift_id', new_shift_id)

    @property
    def action_id(self) -> int:
        return self._action_id

    @action_id.setter
    def action_id(self, new_action_id: int) -> None:
        # Validate inputs
        self.validate_types([(new_action_id, int, 'new_action_id')])

        # If there is no action with the new_action_id, raise ValueError
        if not self.row_exists('action', new_action_id):
            raise ValueError(f'Action<{new_action_id}> does not exist')

        self.set_attribute('action_id', new_action_id)


class Approvals(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS approval (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER,
                shift_id INTEGER,
                action_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id),
                FOREIGN KEY (action_id) REFERENCES action(id)
            )
        ''')

        self.db.commit()
        print('Approvals table created')

    def __init__(self, cur: Cursor, db: Connection) -> None:
        super().__init__(cur, db, 'approval', Approval)

    def add(self, staff_id: int, shift_id: int = 'NULL', action_id: int = 'NULL') -> Approval:
        # Validate inputs
        self.validate_types([(staff_id, int, 'staff_id')])

        # If there is no staff with the staff_id, raise ValueError
        if not self.row_exists('staff', staff_id):
            raise ValueError(f'Staff<{staff_id}> does not exist')

        # If the shift_id is not NULL and there is no shift with the shift_id, raise ValueError
        if shift_id != 'NULL' and not self.row_exists('shift', shift_id):
            raise ValueError(f'Shift<{shift_id}> does not exist')

        # If the action_id is not NULL and there is no action with the action_id, raise ValueError
        if action_id != 'NULL' and not self.row_exists('action', action_id):
            raise ValueError(f'Action<{action_id}> does not exist')

        new_approval_id = self.cur.execute('''
            INSERT INTO approval (staff_id, action_id)
            VALUES (?, ?)
        ''', (staff_id, action_id)).lastrowid

        self.db.commit()

        return Approval(new_approval_id, self.cur, self.db)

    def __repr__(self):
        return f'<Approvals rows={self.rows[0:3]}...>'
