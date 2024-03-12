from sqlite3 import Cursor, Connection

from constants import ACTION_TYPES
from .approval import Approvals
from .base import RowBase, TableBase
from .staff import StaffMembers

ACTION_PERMISSIONS = {
    'create': ['manager', 'bartender', 'server', 'supervisor', 'superuser'],
    'bill_approve': ['supervisor', 'manager', 'superuser'],
    'delete': ['supervisor', 'manager', 'superuser'],
    'update': ['server', 'bartender', 'supervisor', 'manager', 'superuser'],
    'update_bill_items': ['server', 'bartender', 'supervisor', 'manager', 'superuser'],
    'discount': ['supervisor', 'manager', 'superuser'],
    'refund': ['supervisor', 'manager', 'superuser'],
    'void': ['supervisor', 'manager', 'superuser']
}


class Action(RowBase):
    attributes = ['bill_id', 'staff_id', 'approved', 'approval_id', 'type', 'reason']
    table_name = 'action'

    def __init__(self, aid: int, cur: Cursor, db: Connection) -> None:
        self.TYPES = ACTION_TYPES

        super().__init__(aid, cur, db)

        self.__staff_members = StaffMembers(self.cur, self.db)
        self.__approvals = Approvals(self.cur, self.db)

    @property
    def id(self) -> int:
        return self._id

    @property
    def bill_id(self) -> int:
        return self._bill_id

    @bill_id.setter
    def bill_id(self, new_bill_id: int) -> None:
        self.set_attribute('bill_id', new_bill_id)

    @property
    def staff_member(self) -> int | None:
        # If there is no staff member, return None
        if not self._staff_id:
            return None

        return self.__staff_members.get(sid=self._staff_id)

    @staff_member.setter
    def staff_member(self, new_staff_id: int) -> None:
        # If there is no staff member with the new_staff_id, raise ValueError
        staff_member = self.__staff_members.get(sid=new_staff_id)[0]
        if not staff_member:
            raise ValueError(f'Staff<{new_staff_id}> does not exist')

        # Set the staff_id
        self.set_attribute('staff_id', staff_member.id)

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
    def approval(self) -> int:
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
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, new_type: str) -> None:
        # If the new_type is not a valid type, raise ValueError
        if new_type not in self.TYPES:
            raise ValueError(f'Action type must be one of {self.TYPES}, not {new_type}')

        # Validate types
        self.validate_types([(new_type, str, 'new_type')])

        # Set the type
        self.set_attribute('type', new_type)

    @property
    def reason(self) -> str:
        return self._reason

    @reason.setter
    def reason(self, new_reason: str) -> None:
        # Validate types
        self.validate_types([(new_reason, str, 'new_reason')])

        # Set the reason
        self.set_attribute('reason', new_reason)


class Actions(TableBase):
    def create_table(self) -> None:
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS action (
                id INTEGER PRIMARY KEY,
                bill_id INTEGER,
                staff_id INTEGER,
                approved INTEGER,
                approval_id INTEGER,
                type TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bill(id),
                FOREIGN KEY (staff_id) REFERENCES staff_member(id),
                FOREIGN KEY (approval_id) REFERENCES approval(id)
            )
        ''')

        self.db.commit()
        print('Actions table created')

    def __init__(self, cur: Cursor, db: Connection) -> None:
        self.TYPES = ACTION_TYPES
        self.__staff_members = StaffMembers(cur, db)
        super().__init__(cur, db, 'action', Action)

    def add(self, bill_id: int, staff_id: int, approved: bool, approval_id: int, action_type: str,
            reason: str) -> Action:
        # Validate types
        self.validate_types([(bill_id, int, 'bill_id'), (staff_id, int, 'staff_id'), (approved, bool, 'approved'),
                        (approval_id, int, 'approval_id'), (action_type, str, 'type'), (reason, str, 'reason')])

        # If the type is not a valid type, raise ValueError
        if action_type not in self.TYPES:
            raise ValueError(f'Action type must be one of {self.TYPES}, not {action_type}')

        # Get the staff member
        staff_member = self.__staff_members.get(sid=staff_id)[0]
        if not staff_member:
            raise ValueError(f'Staff<{staff_id}> does not exist')

        if staff_member.role.name not in ACTION_PERMISSIONS[action_type]:
            raise ValueError(f'Staff<{staff_id}> does not have permission to perform action<{action_type}>')

        self.cur.execute('''
            INSERT INTO action (bill_id, staff_id, approved, approval_id, type, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bill_id, staff_id, approved, approval_id, action_type, reason))

        self.db.commit()
        print(f'Action added to Bill<{bill_id}>')

        return self.get(bill_id=bill_id, staff_id=staff_id, type=action_type, reason=reason)[0]

    @classmethod
    def add_action(cls, cur, db, bill_id, staff_id, approved, approval_id, action_type, reason):
        actions = cls(cur, db)
        new_action = actions.add(bill_id, staff_id, approved, approval_id, action_type, reason)

        return new_action
