from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from handlers.states import FSMAdmin
from keyboards.admin_kb import make_categories_kb, make_admin_kb, make_lot_management_kb
from misc.others import get_lot_args, show_lot_numbers, compose_lot_text, get_data_for_lot_management
from misc.others import update_lot_from_database, delete_raffled_lot_message, remove_lot_from_database
from misc.others import remove_lot_from_memory, put_a_lot_up_for_auction, complete_auction_lot
from misc.auction_lot import AuctionLot
from my_lib.lite_base import LiteBase


# @dp.message_handler(commands=['Показать_лоты'])
async def show_lot_categories(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Выбери категорию лотов',
            reply_markup=make_categories_kb()
        )


# @dp.message_handler(commands=['Назад'])
async def go_back(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Чего надо хозяин?',
            reply_markup=make_admin_kb()
        )


# @dp.message_handler(commands=['Готовые_к_аукциону'])
async def show_ready_lots(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await show_lot_numbers(message, 'ready_lots')


# @dp.message_handler(commands=['Выставленные'])
async def show_raffled_lots(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await show_lot_numbers(message, 'raffled_lots')


# @dp.message_handler(commands=['Проданные'])
async def show_sold_lots(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await show_lot_numbers(message, 'sold_lots')


# @dp.callback_query_handler(Text(startswith='more'))
async def show_more_lot_info(callback: types.CallbackQuery):
    lot_category, lot_number, chat_id, message_id = get_data_for_lot_management(callback)

    lot_args = get_lot_args(lot_category, lot_number)

    if lot_args:
        lot = AuctionLot(*lot_args)

        await bot.send_photo(
            chat_id,
            photo=lot.main_photo,
            caption=compose_lot_text(lot, lot_category),
            reply_markup=make_lot_management_kb(lot_category, lot_number)
        )


# @dp.callback_query_handler(Text(startswith='to_ready'))
async def move_to_ready(callback: types.CallbackQuery):
    lot_category, lot_number, chat_id, message_id = get_data_for_lot_management(callback)

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id)

    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row(lot_category, 'lot_number', lot_number)

        if lot_data:
            data_base.save_row('ready_lots', *lot_data)

            await delete_raffled_lot_message(data_base, lot_category, lot_number)
            update_lot_from_database(data_base, 'ready_lots', lot_number)
            remove_lot_from_database(data_base, lot_category, lot_number)

    remove_lot_from_memory(lot_number)


# @dp.callback_query_handler(Text(startswith='remove'))
async def remove_lot(callback: types.CallbackQuery):
    lot_category, lot_number, chat_id, message_id = get_data_for_lot_management(callback)

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id)

    with LiteBase('data_base.db') as data_base:
        await delete_raffled_lot_message(data_base, lot_category, lot_number)
        remove_lot_from_database(data_base, lot_category, lot_number)

    remove_lot_from_memory(lot_number)


# @dp.callback_query_handler(Text(startswith='for_auction'))
async def send_lot_for_auction(callback: types.CallbackQuery):
    lot_category, lot_number, chat_id, message_id = get_data_for_lot_management(callback)

    lot_args = get_lot_args(lot_category, lot_number)
    lot = AuctionLot(*lot_args)

    if lot_args:
        photo = await put_a_lot_up_for_auction(lot, chat_id, message_id)

        await lot.start_timer(40)

        if lot in AuctionLot.exhibited_lots:
            await complete_auction_lot(lot, photo)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(show_lot_categories, commands=['Показать_лоты'])
    dp.register_message_handler(go_back, commands=['Назад'])
    dp.register_message_handler(show_ready_lots, commands=['Готовые_к_аукциону'])
    dp.register_message_handler(show_raffled_lots, commands=['Выставленные'])
    dp.register_message_handler(show_sold_lots, commands=['Проданные'])
    dp.register_callback_query_handler(show_more_lot_info, Text(startswith='more'))
    dp.register_callback_query_handler(move_to_ready, Text(startswith='to_ready'))
    dp.register_callback_query_handler(remove_lot, Text(startswith='remove'))
    dp.register_callback_query_handler(send_lot_for_auction, Text(startswith='for_auction'))
