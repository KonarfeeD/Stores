from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import keyboards as kb
from database import *
from aiogram.utils.exceptions import BotBlocked
import dotenv
import os
import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()

dotenv.load_dotenv()
storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    print('Бот запущен!')
    await db_start()


class AddItems(StatesGroup):
    category = State()
    type = State()
    name = State()
    desc = State()
    photo = State()
    price = State()


class DeleteItems(StatesGroup):
    number = State()


class AddToCart(StatesGroup):
    looking = State()
    adding = State()


class SendToAll(StatesGroup):
    creating = State()
    sending = State()


class UX(StatesGroup):
    check_catalog = State()
    check_items = State()
    check_item = State()


class Buy(StatesGroup):
    cart_check = State()
    number = State()
    name = State()
    address = State()


class BuyAll(StatesGroup):
    cart_check = State()
    number = State()
    name = State()
    address = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f'Добро пожаловать, {message.from_user.first_name}!', reply_markup=kb.main)
    user = cur.execute("SELECT a_id FROM accounts WHERE a_id == '{key}'".format(key=message.from_user.id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts VALUES(?, ?, ?, ?)", (message.from_user.id, '', '', ''))
        db.commit()
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы авторизовались как администратор! 🖥', reply_markup=kb.admin_main)


@dp.message_handler(text='Контакты 📲')
async def contacts(message: types.Message):
    await message.answer(f'По всем интересующим вопросам, обращаться по номеру:📲 +998903944839')


@dp.message_handler(text='Назад ◀️', state='*')
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f'Вы вернулись назад ◀️', reply_markup=kb.main)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы авторизовались как администратор! 🖥', reply_markup=kb.admin_main)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'backkk', state='*')
async def backkk(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(chat_id=callback_query.from_user.id, text='Вы вернулись назад ◀️', reply_markup=kb.main)
    if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы авторизовались как администратор! 🖥',
                               reply_markup=kb.admin_main)


@dp.message_handler(text='Добавить товар ™️')
async def add_item(message: types.Message) -> None:
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await AddItems.category.set()
        await message.answer(f'Выберите категорию товара', reply_markup=kb.category)
    else:
        await message.answer(f'Неизвестная команда!')


@dp.message_handler(state=AddItems.category)
async def add_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Мужская одежда 👔':
            data['category'] = 'man'
        elif message.text == 'Женская одежда 👗':
            data['category'] = 'women'
        elif message.text == 'Детская одежда 🧤':
            data['category'] = 'kids'
        elif message.text == 'Для всех':
            data['category'] = 'all'
    await message.reply('Теперь выберите раздел', reply_markup=kb.types)
    await AddItems.next()


@dp.message_handler(state=AddItems.type)
async def add_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Рубашки 👔':
            data['type'] = 'man'
        elif message.text == 'Платья 👗':
            data['type'] = 'women'
        elif message.text == 'Перчатки 🧤':
            data['type'] = 'kids'
        elif message.text == 'Обувь 👟':
            data['type'] = 'shoes'
    await message.reply('Теперь отправьте название товара (только текст!)', reply_markup=kb.cancel)
    await AddItems.next()


@dp.message_handler(state=AddItems.name)
async def add_item_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text

    await message.reply('Теперь отправьте описание товара (только текст!)')
    await AddItems.next()


@dp.message_handler(state=AddItems.desc)
async def add_item_desc(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['desc'] = message.text

    await message.reply('Теперь отправьте фотографию товара (ИМЕННО ФОТО)')
    await AddItems.next()


@dp.message_handler(lambda message: not message.photo, state=AddItems.photo)
async def add_item_check_photo(message: types.Message) -> None:
    await message.reply('Это не фотография!')


@dp.message_handler(content_types=['photo'], state=AddItems.photo)
async def add_item_load_photo(message: types.Message, state: FSMContext) -> None:
    list_photo = []
    for ph in message.photo:
        list_photo.append(ph[-1].file_id)
        print(ph[-1].file_id)
    print(list_photo)
    await message.reply('Теперь отправьте цену (только числа! без пробелов!)')
    await AddItems.next()


@dp.message_handler(state=AddItems.price)
async def add_item_price(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['price'] = message.text
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=data['photo'],
                             caption=f"{data['name']}, {data['desc']}\n{data['price']}")
    await create_tovar(state)
    await message.reply('Товар успешно создан!', reply_markup=kb.admin_main)
    await state.finish()


@dp.message_handler(text='Каталог 👔')
async def catalog(message: types.Message) -> None:
    cur.execute("SELECT name FROM items")
    items = cur.fetchall()
    if not items:
        await message.answer(f'Каталог пуст! 👔')
    else:
        await message.answer('Вы выбрали каталог 👔.', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'Выберите раздел', reply_markup=kb.catalog_buttons())
        await UX.check_catalog.set()


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'add_to_cart', state=UX.check_item)
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        cur.execute("INSERT INTO cart (tg_id, i_id) VALUES (?, ?)", (callback_query.from_user.id, data['tovar']))
        db.commit()
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=f'Товар добавлен в корзину! 🗑',
                               reply_markup=kb.main)
        await state.finish()


@dp.callback_query_handler(state=UX.check_catalog)
async def by_cat(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, text='Товары по выбранной категории:',
                           reply_markup=kb.items_buttons(callback_query.data))
    await UX.check_items.set()


@dp.callback_query_handler(state=UX.check_items)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await UX.check_item.set()
    cur.execute("SELECT * FROM items WHERE i_id == '{key}'".format(key=callback_query.data))
    item = cur.fetchall()
    await bot.send_photo(callback_query.from_user.id, photo=item[0][4],
                         caption=f"Вы выбрали {item[0][1]}!\n\n"
                                 f"{item[0][2]}\n\n"
                                 f"Цена: {item[0][3]} сум", reply_markup=kb.add_to_cart)
    await UX.check_item.set()
    async with state.proxy() as data:
        data['tovar'] = item[0][0]


@dp.message_handler(text='Корзина 🗑')
async def catalog(message: types.Message, state: FSMContext) -> None:
    cur.execute("SELECT * FROM cart WHERE tg_id == {key}".format(key=message.from_user.id))
    item = cur.fetchall()
    print(item)
    if item == []:
        await message.answer(f'Корзина пуста! 🗑')
    else:
        for tovar in item:
            cur.execute("SELECT * FROM items WHERE i_id == {key}".format(key=int(tovar[2])))
            tovar = cur.fetchall()
            await message.answer(f'Товар: {tovar[0][1]}\nЦена: {tovar[0][3]} сум', reply_markup=kb.buy)
            async with state.proxy() as buy_that:
                buy_that['tovar'] = tovar[0][1]
                buy_that['tovar_id'] = tovar[0][0]
                buy_that['user_id'] = message.from_user.id
                buy_that['photo'] = tovar[0][4]
                buy_that['price'] = tovar[0][3]


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'buy')
async def buy(callback_query: types.CallbackQuery):
    await Buy.number.set()
    await bot.send_message(callback_query.from_user.id, f'Отправьте свой номер телефона', reply_markup=kb.cancel)


@dp.message_handler(state=Buy.number)
async def buy_name_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['number'] = message.text
    await message.answer(f'Напишите свое имя', reply_markup=kb.cancel)
    await Buy.next()


@dp.message_handler(state=Buy.name)
async def buy_number_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['name'] = message.text
    await message.answer(f'Теперь введите адрес', reply_markup=kb.location)
    await Buy.next()


@dp.message_handler(content_types=['location'], state=Buy.address)
async def buy_address_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['address'] = message.text
        await bot.send_photo(chat_id=int(os.getenv('GROUP_ID')), photo=buy_that['photo'], caption=f'Купили 🛒: \n'
                                                                                                  f'Цена: {buy_that["price"]}\n'
                                                                                                  f'Номер телефона: {buy_that["number"]}\n'
                                                                                                  f'Имя: {buy_that["name"]}\n')

        await message.forward(chat_id=int(os.getenv('GROUP_ID')))

        cur.execute("DELETE FROM cart WHERE i_id == {key} AND tg_id == {key2}".format(key=int(buy_that['tovar_id']),
                                                                                      key2=int(buy_that['user_id'])))
        db.commit()
    await message.answer(f'Спасибо за заказ! Мы Вам перезвоним в течении часа для уточнения деталей заказа 📲',
                         reply_markup=kb.main)
    await state.finish()


"""
ПОКУПКА ВСЕГО
"""


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'buy_all')
async def buy_all(callback_query: types.CallbackQuery):
    await BuyAll.number.set()
    await bot.send_message(callback_query.from_user.id, f'Отправьте свой номер телефона', reply_markup=kb.cancel)


@dp.message_handler(state=BuyAll.number)
async def buy_all_name_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['number'] = message.text
    await message.answer(f'Напишите свое имя', reply_markup=kb.cancel)
    await BuyAll.next()


@dp.message_handler(state=BuyAll.name)
async def buy_all_number_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['name'] = message.text
    await message.answer(f'Теперь введите адрес', reply_markup=kb.location)
    await BuyAll.next()


@dp.message_handler(content_types=['location'], state=BuyAll.address)
async def buy_all_address_set(message: types.Message, state: FSMContext):
    async with state.proxy() as buy_that:
        buy_that['address'] = message.text

        users_cart = await require_tovar(message.from_user.id)
        for item in users_cart:
            print(item)
            about_item = await check_tovar(item[2])
            print(about_item)
            await bot.send_photo(chat_id=int(os.getenv('GROUP_ID')), photo=about_item[4],
                                 caption=f'Купили 🛒: '
                                         f'{about_item[1]}\n'
                                         f'Цена: {about_item[3]}\n'
                                         f'Номер телефона: {buy_that["number"]}\n'
                                         f'Имя: {buy_that["name"]}\n')
            #
            cur.execute("DELETE FROM cart WHERE i_id == {key} AND tg_id == {key2}".format(key=int(item[2]),
                                                                                          key2=int(
                                                                                              buy_that['user_id'])))
            db.commit()
        await message.forward(chat_id=int(os.getenv('GROUP_ID')))
    await message.answer(f'Спасибо за заказ! Мы Вам перезвоним в течении часа для уточнения деталей заказа 📲',
                         reply_markup=kb.main)
    await state.finish()


@dp.message_handler(text='Сделать рассылку')
async def send_for_all(message: types.Message) -> None:
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await SendToAll.creating.set()
        await message.answer('Введите сообщение', reply_markup=kb.cancel)
    else:
        await message.answer('Неизвестная команда!')


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked_handler(update: types.Update, exception: BotBlocked) -> bool:
    print('Юзер заблокировал бот')
    return True


@dp.message_handler(state=SendToAll.creating)
async def sent_for_all(message: types.Message, state: FSMContext):
    await SendToAll.sending.set()
    cur.execute("SELECT a_id FROM accounts")
    accs = cur.fetchall()
    for i in accs:
        try:
            await bot.send_message(i[0], message.text)
        except Exception as error:
            cur.execute("DELETE FROM accounts WHERE a_id == {key}".format(key=i[0]))
            db.commit()
            print(error)
    await state.finish()
    await message.answer('Рассылка завершена', reply_markup=kb.admin_main)


@dp.message_handler(text='Админ-панель 🖥')
async def admin_panel(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы вошли в админ-панель. 🖥', reply_markup=kb.admin_panel)
    else:
        await message.answer(f'Неизвестная команда!')


@dp.message_handler(text='Удалить товар 🗑')
async def delete_item(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await DeleteItems.number.set()
        await message.answer(f'Выберите товар для удаления', reply_markup=kb.deleting())
    else:
        await message.answer(f'Неизвестная команда!')


@dp.callback_query_handler(state=DeleteItems.number)
async def delete_item_done(callback_query: types.CallbackQuery, state: FSMContext):
    cur.execute("DELETE FROM items WHERE i_id == {key}".format(key=callback_query.data))
    db.commit()
    await bot.send_message(callback_query.from_user.id, f'Удалено!', reply_markup=kb.admin_panel)
    await state.finish()


@dp.message_handler()
async def none(message: types.Message):
    await message.answer(message.chat.id)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)