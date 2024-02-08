from sqlite3 import Cursor, Connection
from helper import validate_types, row_exists
from models.base import TableBase, RowBase


class BillItem(RowBase):
    def __init__(self, bid: int, cur: Cursor, db: Connection):
        attributes = ['bill_id', 'item_id', 'quantity', 'created_by_staff_id', 'staff_note']
        super().__init__(bid, cur, db, 'bill_item', attributes)


    @property
    def bid(self) -> int:
        return self._bid

    @property
    def bill_id(self) -> int:
        return self._bill_id

    @bill_id.setter
    def bill_id(self, new_bill_id: int) -> None:

        # Validate inputs
        validate_types([(new_bill_id, int, 'new_bill_id')])

        # Check if bill exists
        if not row_exists('bill_item', new_bill_id):
            raise ValueError(f'BillItem<{new_bill_id}> does not exist')

        self.set_attribute('bill_id', new_bill_id)

    @property
    def item_id(self) -> int:
        return self._item_id

    @item_id.setter
    def item_id(self, new_item_id: int) -> None:

        # Validate inputs
        validate_types([(new_item_id, int, 'new_item_id')])

        # Check if item exists
        if not row_exists('item', new_item_id):
            raise ValueError(f'Item<{new_item_id}> does not exist')

        self.set_attribute('item_id', new_item_id)

class BillItems(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS bill_item (
                id INTEGER PRIMARY KEY,
                bill_id INTEGER,
                item_id INTEGER,
                quantity INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_staff_id INTEGER,
                staff_note TEXT DEFAULT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bill(id),
                FOREIGN KEY (item_id) REFERENCES item(id),
                FOREIGN KEY (created_by_staff_id) REFERENCES staff(id)
            )
        ''')

    def __init__(self, cur: Cursor, db: Connection):
       super().__init__(cur, db, 'bill_item', BillItem, 'bid')

    def add(self, bill_id: int, item_id: int, staff_id: int, staff_note: str = 'NULL'):
        self.cur.execute('''
            INSERT INTO bill_item (bill_id, item_id, created_by_staff_id, staff_note)
            VALUES (?, ?, ?)
        ''', (bill_id, item_id, staff_id, staff_note))
        self.db.commit()

        new_bill_item = BillItem(self.cur.lastrowid, self.cur, self.db)

        return new_bill_item