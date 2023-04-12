import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts(a_id INTEGER PRIMARY KEY, cart_id TEXT, phone TEXT, address TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS items(i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT, desc TEXT, price TEXT, photo TEXT, brand TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cart(с_id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER, i_id INTEGER)")
    db.commit()


async def create_tovar(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['category']))
        db.commit()

async def delete_tovar(data, state):
    async with state.proxy() as data:
        cur.execute("DELETE FROM items WHERE name == ? (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                (data['name'], data['desc'], data['price'], data['photo'], data['category']))
        db.commit()

async def require_tovar(user_id):
    items_from_cart = cur.execute("SELECT * FROM cart WHERE tg_id == {key}".format(key=user_id)).fetchall()
    return items_from_cart
