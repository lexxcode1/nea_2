import random
import time

from connector import connect
from models import Items, Menus
from models.menuitem import MenuItems

# Connect to the database
db = connect()

# Create the cursor
cur = db.cursor()

# Create the menu items
print('HERE')
items = Items(cur, db)
print('THERE')
# Time this
start = time.time()
item = random.choice(items.get())
end = time.time()
print(end - start)

print(f'item: {item} description: {item.description}')

# Create the menu items
menu_items = MenuItems(cur, db)
menus = Menus(cur,db)

menu = random.choice(menus.get())

print(f'menu: {menu} name: {menu.name}')

menu.add_item(item.id)

print(f'menu_item<item_id={item.id}>: {menu_items.get(item_id=item.id)}')
# print('get menu_id=1',menu_items.get(menu_id=1))
print(menu_items.get(True, menu_id=6))
