from datetime import datetime

from .action import Actions
from .approval import Approvals
from .base import RowBase, TableBase
from .staff import StaffMembers


class Shift(RowBase):
    attributes = ['staff_id', 'started_at', 'ended_at', 'break_started_at', 'break_ended_at', 'approved',
                  'approval_id']
    table_name = 'shift'

    def __init__(self, shift_id: int, cur, db) -> None:

        self.__approvals = Approvals(self.cur, self.db)
        self.__staff_members = StaffMembers(self.cur, self.db)
        self.__actions = Actions(self.cur, self.db)

        super().__init__(shift_id, cur, db)

    @property
    def id(self) -> int:
        return self._id

    @property
    def staff_member(self):
        # If there is no staff member, return None
        if not self._staff_id:
            return None

        return self.__staff_members.get(sid=self._staff_id)[0]

    @staff_member.setter
    def staff_member(self, new_staff_id: int) -> None:
        # If there is no staff member with the new_staff_id, raise ValueError
        staff_member = self.__staff_members.get(sid=new_staff_id)[0]
        if not staff_member:
            raise ValueError(f'Staff<{new_staff_id}> does not exist')

        # Set the staff_id
        self.set_attribute('staff_id', staff_member.id)

    @staticmethod
    def __handle_date(date: datetime) -> str:
        date = date[0: date.rfind('.')]
        if type(date) is str:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        # Validate types
        self.validate_types([(date, datetime, 'date')])

        # If date is in the future, raise a ValueError
        if date > datetime.now():
            raise ValueError(f'Created at must be in the past, not {date}')
        return date

    @property
    def started_at(self) -> datetime:
        return datetime.strptime(self._started_at, '%Y-%m-%d %H:%M:%S') if type(
            self._started_at) is str else self._started_at

    @started_at.setter
    def started_at(self, new_started_at: datetime) -> None:
        new_started_at = self.__handle_date(new_started_at)

        self.set_attribute('started_at', new_started_at)

    @property
    def ended_at(self) -> datetime:
        return datetime.strptime(self._ended_at, '%Y-%m-%d %H:%M:%S') if type(
            self._ended_at) is str else self._ended_at

    @ended_at.setter
    def ended_at(self, new_ended_at: datetime) -> None:
        new_ended_at = self.__handle_date(new_ended_at)

        self.set_attribute('ended_at', new_ended_at)

    @property
    def break_started_at(self) -> datetime:
        return datetime.strptime(self._break_started_at, '%Y-%m-%d %H:%M:%S') if type(
            self._break_started_at) is str else self._break_started_at

    @break_started_at.setter
    def break_started_at(self, new_break_started_at: datetime) -> None:
        new_break_started_at = self.__handle_date(new_break_started_at)

        self.set_attribute('break_started_at', new_break_started_at)

    @property
    def break_ended_at(self) -> datetime:
        return datetime.strptime(self._break_ended_at, '%Y-%m-%d %H:%M:%S') if type(
            self._break_ended_at) is str else self._break_ended_at

    @break_ended_at.setter
    def break_ended_at(self, new_break_ended_at: datetime) -> None:
        new_break_ended_at = self.__handle_date(new_break_ended_at)

        self.set_attribute('break_ended_at', new_break_ended_at)

    @property
    def approved(self) -> bool:
        return self._approved if type(self._approved) is bool else bool(self._approved)

    @approved.setter
    def approved(self, new_approved: bool) -> None:
        # Change int bool to bool
        if type(new_approved) is int:
            new_approved = bool(new_approved)

        # Validate types
        self.validate_types([(new_approved, bool, 'new_approved')])

        # Set the approved
        self.set_attribute('approved', new_approved)

    @property
    def approval(self):
        # Check if the approval exists
        if not self._approval_id or self._approval_id == 'NULL':
            return None

        return self.__approvals.get(aid=self._approval_id)[0]

    @approval.setter
    def approval(self, new_approval_id: int) -> None:
        # If there is no approval with the new_approval_id, raise ValueError
        approval = self.__approvals.get(aid=new_approval_id)[0]
        if not approval:
            raise ValueError(f'Approval<{new_approval_id}> does not exist')

        # Set the approval_id
        self.set_attribute('approval_id', approval.id)

    @property
    def shift_length(self):
        return self.ended_at - self.started_at

    @property
    def break_length(self):
        return self.break_ended_at - self.break_started_at

    @property
    def total_hours(self):
        return (self.shift_length - self.break_length).seconds / 3600

    @property
    def total_pay(self):
        return self.staff_member.wage * self.total_hours

    def approve_shift(self, staff_id: int):
        # If the shift is already approved, return
        if self.approved:
            return

        # Get the allowed roles to approve shifts
        allowed_to_approve = ['manager', 'superuser']

        # If the staff_id is not permitted, raise ValueError
        if not self.__staff_members.get(sid=staff_id)[0].role not in allowed_to_approve:
            raise ValueError(f'Staff<{staff_id}> is not allowed to approve shifts')

        self.approval = self.__approvals.add(staff_id, shift_id=self.id)

        self.approved = True


class Shifts(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS shift (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER,
                started_at DATETIME,
                ended_at DATETIME,
                break_started_at DATETIME,
                break_ended_at DATETIME,
                approved INTEGER DEFAULT 0,
                approval_id INTEGER DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id),
                FOREIGN KEY (approval_id) REFERENCES approval(id)
            )
        ''')

        self.db.commit()
        print('Shifts table created')

    def __init__(self, cur, db):
        super().__init__(cur, db, 'shift', Shift)

    def add(self, staff_id: int, started_at: datetime, ended_at: datetime, break_started_at: datetime,
            break_ended_at: datetime):
        # Validate types
        self.validate_types([(staff_id, int, 'staff_id')])

        # If there is no staff with the staff_id, raise ValueError
        if not self.row_exists('staff', staff_id):
            raise ValueError(f'Staff<{staff_id}> does not exist')

        # If the started_at is after the ended_at, raise ValueError
        if started_at > ended_at:
            raise ValueError(f'started_at must be before ended_at, not {started_at} and {ended_at}')

        # If the break_started_at is after the break_ended_at, raise ValueError
        if break_started_at > break_ended_at:
            raise ValueError(
                f'break_started_at must be before break_ended_at, not {break_started_at} and {break_ended_at}')

        # If the break_started_at is before the started_at, raise ValueError
        if break_started_at < started_at:
            raise ValueError(f'break_started_at must be after started_at, not {break_started_at} and {started_at}')

        # If the break_ended_at is after the ended_at, raise ValueError
        if break_ended_at > ended_at:
            raise ValueError(f'break_ended_at must be before ended_at, not {break_ended_at} and {ended_at}')

        # Add the shift to the database
        new_shift_id = self.cur.execute('''
            INSERT INTO shift (staff_id, started_at, ended_at, break_started_at, break_ended_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (staff_id, started_at, ended_at, break_started_at, break_ended_at)).lastrowid

        self.db.commit()

        return Shift(new_shift_id, self.cur, self.db)

    @property
    def unapproved_shifts(self):
        return self.get(approved=False)

    @property
    def currently_on_shift(self):
        return self.get(True, started_at_between=(datetime.fromtimestamp(1), datetime.now()), ended_at=None)
