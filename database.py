import sqlite3 as sq


async def db_start():
    global db, cur
    db = sq.connect('tg.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts(a_id INTEGER PRIMARY KEY, cart_id TEXT, phone TEXT, address TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS items(i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT, desc TEXT, price TEXT, photo TEXT, brand TEXT, types TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cart(с_id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER, i_id INTEGER)")
    db.commit()


async def create_tovar(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, photo, brand, types) VALUES (?, ?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['category'], data['type']))
    db.commit()


async def choose_type(state):
    async with state.proxy() as data:
        cur.execute("SELECT * FROM items WHERE types == ? (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['category']))
        db.commit()


async def delete_tovar(state):
    async with state.proxy() as data:
        cur.execute("DELETE FROM items WHERE name == ? (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['category']))
        db.commit()


async def require_tovar(user_id):
    items_from_cart = cur.execute("SELECT * FROM cart WHERE tg_id == {key}".format(key=user_id)).fetchall()
    return items_from_cart


async def check_tovar(item_id):
    item_id = cur.execute("SELECT * FROM items WHERE i_id == {key}".format(key=item_id)).fetchone()
    return item_id