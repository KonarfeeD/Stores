from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, \
    KeyboardButton
import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог 👔').add('Корзина 🗑').add('Контакты 📲')

admin_main = ReplyKeyboardMarkup(resize_keyboard=True)
admin_main.add('Каталог 👔').add('Корзина 🗑').add('Контакты 📲').add('Админ-панель 🖥')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар ™️').add('Удалить товар 🗑').add('Сделать рассылку').add('Назад ◀️')

category = ReplyKeyboardMarkup(resize_keyboard=True)
category.add("Мужская одежда 👔").add("Женская одежда 👗").add("Детская одежда 🧤").add('Для всех').add('Назад ◀️')

types = ReplyKeyboardMarkup(resize_keyboard=True)
types.add("Рубашки 👔").add("Платья 👗").add("Перчатки 🧤").add('Обувь 👟').add('Назад ◀️')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Назад ◀️')

location = ReplyKeyboardMarkup(resize_keyboard=True)
location.add(KeyboardButton('Отправить геолокацию!', request_location=True)).add(KeyboardButton('Назад ◀️'))

#  ------------------------------------------------------------------
"""
Скрипт создания онлайн кнопок в каталоге с помощью перебора всех имён в БД
"""


def catalog_buttons():
    buttons = []
    cur.execute("SELECT brand FROM items")
    brand = cur.fetchall()

    brand_list = []

    for tpl in brand:
        brand_list.append(list(tpl))

    for item in brand_list:
        if item[0] == 'man':
            item.append('Мужская одежда 👔')
        elif item[0] == 'women':
            item.append('Женская одежда 👗')
        elif item[0] == 'kids':
            item.append('Детская одежда 🧤')
        elif item[0] == 'all':
            item.append('Для всех')
        button = InlineKeyboardButton(item[1], callback_data=item[0])
        buttons.append(button)
    catalog = InlineKeyboardMarkup(row_width=2)
    return catalog.add(*set(buttons), InlineKeyboardButton('Назад ◀️', callback_data='backkk'))


def under_catalog_buttons():
    buttons = []
    cur.execute("SELECT types FROM items")
    brand = cur.fetchall()

    brand_list = []

    for tpl in brand:
        brand_list.append(list(tpl))

    for item in brand_list:
        if item[0] == 'man':
            item.append('Рубашки 👔')
        elif item[0] == 'women':
            item.append('Платья 👗')
        elif item[0] == 'kids':
            item.append('Перчатки 🧤')
        elif item[0] == 'shoes':
            item.append('Обувь 👟')
        button = InlineKeyboardButton(item[1], callback_data=item[0])
        buttons.append(button)
    catalog = InlineKeyboardMarkup(row_width=2)
    return catalog.add(*set(buttons), InlineKeyboardButton('Назад ◀️', callback_data='backkk'))




def items_buttons(tovar):
    items_buttons = []
    cur.execute(f"SELECT i_id, name FROM items WHERE brand = '{tovar}';")
    itemz = cur.fetchall()
    for item in itemz:
        button = InlineKeyboardButton(item[1], callback_data=item[0])
        items_buttons.append(button)

    catalog = InlineKeyboardMarkup(row_width=2)
    return catalog.add(*items_buttons, InlineKeyboardButton('Назад ◀️', callback_data='backkk'))


def deleting():
    deleting_buttons = []
    cur.execute('SELECT name, i_id FROM items')
    ditems = cur.fetchall()
    for ditem in ditems:
        button = InlineKeyboardButton(ditem[0], callback_data=ditem[1])
        deleting_buttons.append(button)

    dcatalog = InlineKeyboardMarkup(row_width=2)
    return dcatalog.add(*deleting_buttons)


#  ------------------------------------------------------------------

add_to_cart = InlineKeyboardMarkup(row_width=2)
add_to_cart.add(InlineKeyboardButton('Добавить в корзину 🗑', callback_data='add_to_cart'),
                InlineKeyboardButton('Назад ◀️', callback_data='backkk'))

buy = InlineKeyboardMarkup(row_width=1)
buy.add(InlineKeyboardButton('Купить 🛒', callback_data='buy'),
        InlineKeyboardButton('Купить всё 🛒', callback_data='buy_all'))