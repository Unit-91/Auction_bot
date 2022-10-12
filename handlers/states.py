from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from create_bot import bot, CHAT_OWNER_ID
from my_lib.lite_base import LiteBase
from my_lib.different_funcs import convert_list_to_string
from keyboards.admin_kb import make_admin_kb, make_cancel_kb, make_stop_kb


def save_lot(data):
    addit_media = convert_list_to_string(data['addit_media'])

    lot_tuple = (
        int(data['lot_number']), int(data['auction_time']),
        int(data['start_price']), None, data['main_photo'],
        addit_media, data['description'], None, None
    )

    with LiteBase('data_base.db') as data_base:
        data_base.save_row('ready_lots', *lot_tuple)


class FSMAdmin(StatesGroup):
    admin_ids = [CHAT_OWNER_ID]

    lot_number = State()
    auction_time = State()
    price = State()
    main_photo = State()
    additional_media = State()
    description = State()


# @dp.message_handler(commands=['admin'])
async def send_admin_keyboard(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Чего надо хозяин?',
            reply_markup=make_admin_kb()
        )
        await message.delete()


# @dp.message_handler(commands=['Загрузить_лот'], state=None)
async def start_loading_lot(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await FSMAdmin.lot_number.set()
        await message.reply('Напиши номер лота', reply_markup=make_cancel_kb())


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_lot_loading(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        current_state = await state.get_state()

        if current_state is None:
            return

        await state.finish()
        await message.reply('Загрузка лота отменена', reply_markup=make_admin_kb())


# @dp.message_handler(state=FSMAdmin.lot_number)
async def load_lot_number(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['lot_number'] = message.text
            data['addit_media'] = []

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
            'Загрузи дополнительные фото и видео. Нажми хватит если загрузил все',
            reply_markup=make_stop_kb()
        )


# @dp.message_handler(content_types=['photo', 'video'], state=FSMAdmin.additional_media)
async def load_additional_media(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:

        async with state.proxy() as data:
            if message.content_type == 'photo':
                data['addit_media'].append('photo_' + message.photo[-1].file_id)
            else:
                data['addit_media'].append('video_' + message.video.file_id)

            media_len = len(data['addit_media'])

        await message.reply(media_len)


# @dp.message_handler(commands=['Хватит'], state=FSMAdmin.additional_media)
async def stop_load_additional_media(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        await FSMAdmin.next()

        await bot.send_message(
            message.from_user.id,
            'Загрузи полное описание',
            reply_markup=make_cancel_kb()
        )


# @dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['description'] = message.text

        save_lot(data)

        await state.finish()

        await bot.send_message(
            message.from_user.id,
            'Лот загружен',
            reply_markup=make_admin_kb()
        )


def register_states_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_keyboard, commands=['admin'])
    dp.register_message_handler(start_loading_lot, commands=['Загрузить_лот'], state=None)
    dp.register_message_handler(cancel_lot_loading, state="*", commands='отмена')
    dp.register_message_handler(cancel_lot_loading, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_lot_number, state=FSMAdmin.lot_number)
    dp.register_message_handler(load_auction_time, state=FSMAdmin.auction_time)
    dp.register_message_handler(load_start_price, state=FSMAdmin.price)
    dp.register_message_handler(load_main_photo, content_types=['photo'], state=FSMAdmin.main_photo)
    dp.register_message_handler(load_additional_media, content_types=['photo', 'video'], state=FSMAdmin.additional_media)
    dp.register_message_handler(stop_load_additional_media, commands=['Хватит'], state=FSMAdmin.additional_media)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
