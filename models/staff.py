from datetime import datetime, timedelta

from facades.bill_only import get_all_bills_created_by_staff_member, add_bill

from models.base import RowBase, TableBase
from models.role import Roles, Role


class StaffMember(RowBase):
    table_name = 'staff_member'
    attributes = ['name', 'role_id', 'wage']

    def __init__(self, staff_id: int, cur, db) -> None:
        from models import Bookings

        super().__init__(staff_id, cur, db)

        self.__bookings = Bookings(self.cur, self.db)
        self.__roles = Roles(self.cur, self.db)

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

    @property
    def wage(self) -> float:
        return self._wage

    @wage.setter
    def wage(self, new_wage: float) -> None:
        # Validate types
        self.validate_types([(new_wage, float, 'new_wage')])

        # If new_wage is less than 0, raise ValueError
        if new_wage < 0:
            raise ValueError('new_wage must be greater than 0')

        # Set the wage
        self.set_attribute('wage', new_wage)

    def add_bill(self, customer_id: int = None, seat_id: int = None):
        add_bill(self.cur, self.db, customer_id, seat_id, self.id)

    def create_action(self):
        pass

    def approve_action(self):
        pass

    def approve_shift(self):
        pass

    def void_item(self):
        pass

    def add_items(self):
        pass

    def add_action(self):
        pass

    def start_shift(self):
        pass

    def end_shift(self):
        pass

    def start_break(self):
        pass

    def end_break(self):
        pass

    def get_total_hours_between(self, start: datetime, end: datetime) -> timedelta:
        pass

    def get_shifts_between(self, start: datetime, end: datetime) -> timedelta:
        pass

    def calculate_pay_between(self, start: datetime, end: datetime) -> float:
        pass

    def fire(self):
        # Delete the staff member
        del self

    @property
    def role(self):
        return self.__roles.get(rid=self._role_id)

    @role.setter
    def role(self, new_role: Role | None):
        if not new_role:
            new_role = 'NULL'

        if not self.row_exists('role', new_role.id if new_role != 'NULL' else -1):
            raise ValueError(f'Role<{new_role}> does not exist')

        self.set_attribute('role_id', new_role.id)

    @property
    def bills_created(self):
        return get_all_bills_created_by_staff_member(self.id, self.cur, self.db)

    @property
    def actions(self):
        pass

    @property
    def assigned_bookings(self):
        assigned = self.__bookings.get(assigned_staff_member_id=self.id)

        return assigned if assigned else None


class StaffMembers(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS staff_member (
                id INTEGER PRIMARY KEY,
                name TEXT,
                role_id INTEGER,
                wage REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.db.commit()
        print('StaffMembers table created')

    def __init__(self, cur, db):
        from helper import row_exists

        self.row_exists = row_exists
        super().__init__(cur, db, 'staff_member', StaffMember)

    def add(self, name: str, role_id: int, wage: float) -> StaffMember:
        # Validate types
        self.validate_types([(name, str, 'name'), (role_id, int, 'role_id'), (wage, float, 'wage')])

        # If name is not between 1 and 25 characters long, raise ValueError
        if len(name) < 1 or len(name) > 25:
            raise ValueError('name must be between 1 and 25 characters long')

        # If role_id is not a valid role, raise ValueError
        if not self.row_exists('role', role_id):
            raise ValueError(f'Role<{role_id}> does not exist')

        # If wage is less than 0, raise ValueError
        if wage < 0:
            raise ValueError('wage must be greater than 0')

        # Add the staff member
        self.cur.execute('''
            INSERT INTO staff_member (name, role_id, wage)
            VALUES (?, ?, ?)
        ''', (name, role_id, wage))
        self.db.commit()
        print('StaffMember added')

        new_staff_member = StaffMember(self.cur.lastrowid, self.cur, self.db)

        return new_staff_member
        pass
