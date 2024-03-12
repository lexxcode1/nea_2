from sqlite3 import Cursor, Connection

from models.base import RowBase, TableBase
from models.menuitem import MenuItems, MenuItem


class Menu(RowBase):
    attributes = ['name', 'active', 'max_size']
    table_name = 'menu'

    def __init__(self, menu_id: int, cur: Cursor, db: Connection) -> None:

        super().__init__(menu_id, cur, db)

        # Initialize the MenuItems
        self.__menu_items = MenuItems(self.cur, self.db)

        # Set the relationship variables
        self._items = []

    @property
    def id(self) -> int:
        """
        Get the id of the Menu

        :return int : id of the Menu
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the name of the Menu

        :return str : name of the Menu
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Set the name of the Menu

        :param new_name: str New name of the Menu
        :return None:
        """
        # Validate types
        self.validate_types([(new_name, str, 'new_name')])

        # If new_name is the same as the current name, return
        if new_name == self._name:
            return

        # If new_name is shorter than 1 character, raise ValueError
        if len(new_name) < 1 or len(new_name) > 25:
            raise ValueError('new_name must be between 1 and 25 characters long')

        self.set_attribute('name', new_name)

    @property
    def active(self) -> bool:
        """
        Get the active status of the Menu

        :return bool : active status of the Menu
        """
        if type(self._active) is int:
            return bool(self._active)
        return self._active

    @active.setter
    def active(self, new_active: bool) -> None:
        """
        Set the active status of the Menu

        :param new_active: bool New active status of the Menu
        :return None:
        """
        # Validate types
        self.validate_types([(new_active, bool, 'new_active')])

        self.set_attribute('active', new_active)

    @property
    def max_size(self) -> int:
        """
        Get the max_size of the Menu

        :return int : max_size of the Menu
        """
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size: int) -> None:
        """
        Set the max_size of the Menu

        :param new_max_size: int New max_size of the Menu
        :return None:
        """
        # Validate types
        self.validate_types([(new_max_size, int, 'new_max_size')])

        # If new_max_size is less than 1, raise ValueError
        if new_max_size < 0:
            raise ValueError('new_max_size must be greater than 0')

        self.set_attribute('max_size', new_max_size)

    @property
    def current_size(self) -> int:
        """
        Get the current_size of the Menu

        :return int : current_size of the Menu
        """
        # get how many item are in associated with the menu
        # TODO implement when items & Menuitem are implemented
        return 1

    @current_size.setter
    def current_size(self, new_current_size: int) -> None:
        pass

    @property
    def full(self) -> bool:
        """
        Get the full status of the Menu

        :return bool : full status of the Menu
        """
        return self.current_size >= self.max_size

    @property
    def items(self) -> list:
        """
        Get the items associated with the Menu

        :return list : items associated with the Menu
        """
        return self.__menu_items.get(menu_id=self.id)

    def add_item(self, item_id: int) -> MenuItem | None:
        """
        Add an item to the Menu

        :param item_id: int id of the Item to add
        :return None:
        """
        # Validate inputs
        self.validate_types([(item_id, int, 'item_id')])

        # If item_id is not a valid item, raise ValueError
        if not self.row_exists('item', item_id):
            raise ValueError(f'Item<{item_id}> does not exist')

        # If there is already a MenuItem with the same item_id, return
        if len(self.__menu_items.get(True, item_id=item_id, menu_id=self.id)) > 0:
            print('fm', self.__menu_items.get(True, item_id=item_id, menu_id=self.id))
            return

        # If the menu is full, raise ValueError
        if self.full:
            raise ValueError(f'Menu<{self.id}> is full')

        # Add the item to the Menu
        return self.__menu_items.add(self.id, item_id)

    def remove_item(self, item_id: int) -> None:
        """
        Remove an item from the Menu

        :param item_id: int id of the Item to remove
        :return None:
        """
        # Validate inputs
        self.validate_types([(item_id, int, 'item_id')])

        # If item_id is not a valid item, raise ValueError
        if not self.row_exists('item', item_id):
            raise ValueError(f'Item<{item_id}> does not exist')

        # Get the MenuItem with the item_id
        menu_item = self.__menu_items.get(item_id=item_id, menu_id=self.id)

        # If there is no MenuItem with the item_id, return
        if not menu_item: return

        # Remove the item from the Menu
        self.__menu_items.delete(menu_item.id)

        return menu_item

    def __hash__(self):
        return hash(self.id)


    def __repr__(self):
        return f'<Menu id={self.id}, name={self.name}, active={self.active}, max_size={self.max_size}, current_size={self.current_size}, full={self.full}>'


class Menus(TableBase):
    def __init__(self, cur: Cursor, db: Connection):
        super().__init__(cur, db, 'menu', Menu)

    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY,
                name TEXT,
                active INTEGER DEFAULT 1,
                max_size INTEGER DEFAULT 100,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.db.commit()
        print('Menu table created')

    def add(self, name: str, active: bool, max_size: int) -> Menu:
        """
        Add a new Menu to the database
        :param name: str name of the new Menu
        :param active: bool whether the Menu is active
        :param max_size: int max size of the Menu
        :return Menu: new Menu object
        """
        # Validate inputs
        self.validate_types([(name, str, 'name'), (active, bool, 'active'), (max_size, int, 'max_size')])

        # Insert the new Menu into the database
        self.cur.execute('''
            INSERT INTO menu (name, active, max_size)
            VALUES (?, ?, ?)
        ''', (name, int(active), max_size))

        # Commit the changes
        self.db.commit()

        # Get the id of the new Menu
        new_menu = Menu(self.cur.lastrowid, self.cur, self.db)

        return new_menu

    def __repr__(self):
        return f'<Menus rows={self.rows[0:5]}...>'
