from .base import RowBase, TableBase
from .menu import Menus


class MenuItem(RowBase):
    def __init__(self, mid: int, cur, db) -> None:
        attributes = ['menu_id', 'item_id']
        super().__init__(mid, cur, db, 'menu_item', attributes)

    @property
    def mid(self) -> int:
        return self._id

    @property
    def menu_id(self) -> int:
        return self._menu_id

    @menu_id.setter
    def menu_id(self, new_menu_id: int) -> None:
        self.set_attribute('menu_id', new_menu_id)

    @property
    def item_id(self) -> int:
        return self._item_id

    @item_id.setter
    def item_id(self, new_item_id: int) -> None:
        self.set_attribute('item_id', new_item_id)


class MenuItems(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_item (
                id INTEGER PRIMARY KEY,
                menu_id INTEGER,
                item_id INTEGER,
                FOREIGN KEY (menu_id) REFERENCES menu(id),
                FOREIGN KEY (item_id) REFERENCES item(id)
            )
        ''')

        self.db.commit()
        print('MenuItems table created')

    def __init__(self, cur, db):
        super().__init__(cur, db, 'menu_item', MenuItem, 'mid')

    def add(self, menu_id: int, item_id: int) -> MenuItem:
        self.cur.execute('''
            INSERT INTO menu_item (menu_id, item_id)
            VALUES (?, ?)
        ''', (menu_id, item_id))

        # Check if the menu is full
        if Menus(self.cur, self.db).get(menu_id=menu_id).full:
            raise ValueError(f'Menu<{menu_id}> is full')

        self.db.commit()
        print(f'MenuItem added to Menu<{menu_id}>')

        new_menu_item = MenuItem(self.cur.lastrowid, self.cur, self.db)

        return new_menu_item

    def __repr__(self):
        return f'<MenuItems rows={self.rows[0:3]}...>'
