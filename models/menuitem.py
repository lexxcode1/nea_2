from .base import RowBase, TableBase


class MenuItem(RowBase):
    attributes = ['menu_id', 'item_id']
    table_name = 'menu_item'
    def __init__(self, menu_item_id: int, cur, db) -> None:
        super().__init__(menu_item_id, cur, db)

    @property
    def id(self) -> int:
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

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'<MenuItem id={self.id} menu_id={self.menu_id} item_id={self.item_id}>'


class MenuItems(TableBase):
    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_item (
                id INTEGER PRIMARY KEY,
                menu_id INTEGER,
                item_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (menu_id) REFERENCES menu(id),
                FOREIGN KEY (item_id) REFERENCES item(id)
            )
        ''')

        self.db.commit()
        print('MenuItems table created')

    def __init__(self, cur, db):
        super().__init__(cur, db, 'menu_item', MenuItem)

    def add(self, menu_id: int, item_id: int) -> MenuItem:
        from .menu import Menus

        self.cur.execute('''
            INSERT INTO menu_item (menu_id, item_id)
            VALUES (?, ?)
        ''', (menu_id, item_id))

        # Check if the menu is full
        if Menus(self.cur, self.db).get(mid=menu_id)[0].full:
            raise ValueError(f'Menu<{menu_id}> is full')

        self.db.commit()
        print(f'Item<{item_id}> added to Menu<{menu_id}>')

        new_menu_item = MenuItem(self.cur.lastrowid, self.cur, self.db)

        return new_menu_item

    def __repr__(self):
        return f'<MenuItems rows={self.rows[0:3]}...>'
