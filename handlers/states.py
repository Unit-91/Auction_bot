from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from create_bot import bot, data_base
from keyboards.admin_kb import make_admin_keyboard, make_cancel_keyboard, make_stop_keyboard


class AdminMediaStorage():
    def __init__(self, admin_id):
        self.admin_id = admin_id
        self.photos = []
        self.videos = []


class FSMAdmin(StatesGroup):
    admin_ids = []
    admin_storages = []

    lot_number = State()
    auction_time = State()
    price = State()
    main_photo = State()
    other_photos = State()
    videos = State()
    full_description = State()


# @dp.message_handler(commands=['admin'], is_chat_admin=True)
async def send_admin_keyboard(message: types.Message):
    if message.from_user.id not in FSMAdmin.admin_ids:
        FSMAdmin.admin_ids.append(message.from_user.id)

    FSMAdmin.admin_storages.append(AdminMediaStorage(message.from_user.id))

    await bot.send_message(
        message.from_user.id,
        'Чего надо хозяин?',
        reply_markup=make_admin_keyboard()
    )
    await message.delete()


# @dp.message_handler(commands=['Загрузить_лот'], state=None)
async def start_loading_lot(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await FSMAdmin.lot_number.set()
        await message.reply('Напиши номер лота', reply_markup=make_cancel_keyboard())


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_lot_loading(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        current_state = await state.get_state()

        if current_state is None:
            return

        for storage in FSMAdmin.admin_storages:
            if storage.admin_id == message.from_user.id:
                FSMAdmin.admin_storages.remove(storage)

        await state.finish()
        await message.reply('Загрузка лота отменена', reply_markup=make_admin_keyboard())


# @dp.message_handler(state=FSMAdmin.lot_number)
async def load_lot_number(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['lot_number'] = message.text

        await FSMAdmin.next()
        await message.reply("Загрузи время аукциона")


# @dp.message_handler(state=FSMAdmin.auction_time)
async def load_auction_time(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['auction_time'] = message.text

        await FSMAdmin.next()
        await message.reply("Загрузи стартовую цену")


# @dp.message_handler(state=FSMAdmin.price)
async def load_start_price(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['start_price'] = message.text

        await FSMAdmin.next()
        await message.reply("Загрузи главное фото")


# @dp.message_handler(content_types=['photo'], state=FSMAdmin.main_photo)
async def load_main_photo(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['main_photo'] = message.photo[-1].file_id

        await FSMAdmin.next()
        await bot.send_message(
            message.from_user.id,
            'Загрузи фото альбом. Нажми хватит, если загрузил все фото',
            reply_markup=make_stop_keyboard()
        )


# @dp.message_handler(content_types=['photo'], state=FSMAdmin.other_photos)
async def load_other_photos(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        photos = None

        for storage in FSMAdmin.admin_storages:
            if storage.admin_id == message.from_user.id:
                photos = storage.photos
                photos.append(message.photo[-1].file_id)

        async with state.proxy() as data:
            data['other_photos'] = photos
            await message.reply(len(photos))
            print(photos)


# @dp.message_handler(commands=['Хватит'], state=FSMAdmin.other_photos)
async def stop_load_other_photos(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        await FSMAdmin.next()

        await bot.send_message(
            message.from_user.id,
            'Теперь загрузи видео альбом. Нажми хватит, если загрузил все видео',
            reply_markup=make_stop_keyboard()
        )


def register_states_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_keyboard, commands=['admin'], is_chat_admin=True)
    dp.register_message_handler(start_loading_lot, commands=['Загрузить_лот'], state=None)
    dp.register_message_handler(cancel_lot_loading, state="*", commands='отмена')
    dp.register_message_handler(cancel_lot_loading, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_lot_number, state=FSMAdmin.lot_number)
    dp.register_message_handler(load_auction_time, state=FSMAdmin.auction_time)
    dp.register_message_handler(load_start_price, state=FSMAdmin.price)
    dp.register_message_handler(load_main_photo, content_types=['photo'], state=FSMAdmin.main_photo)
    dp.register_message_handler(load_other_photos, content_types=['photo'], state=FSMAdmin.other_photos)
    dp.register_message_handler(stop_load_other_photos, commands=['Хватит'], state=FSMAdmin.other_photos)
