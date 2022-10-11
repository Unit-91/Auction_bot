from aiogram import types, Dispatcher
from create_bot import bot, CHAT_ID
from aiogram.dispatcher.filters import Text
from handlers.states import FSMAdmin
from keyboards.admin_kb import make_categories_kb, make_admin_kb, make_more_lot_info_kb, make_lot_management_kb
from keyboards.client_kb import make_auction_keyboard
from misc.others import get_lot_args, conv_bidders_to_str, conv_winner_to_str
from misc.auction_lot import AuctionLot
from my_lib.lite_base import LiteBase


async def show_lot_numbers(message, lot_category):
    with LiteBase('data_base.db') as data_base:
        lst = data_base.load_all_columns('lot_number', lot_category)

    if lst:
        for lot_number in lst:
            await bot.send_message(
                message.from_user.id,
                text=f'Лот № {lot_number}',
                reply_markup=make_more_lot_info_kb(lot_category, lot_number)
            )
    else:
        await message.answer('В этой категории нет лотов')


def compose_lot_text(lot, lot_category):
    if lot_category == 'ready_lots':
        lot.create_text()

    if lot_category == 'raffled_lots':
        if lot.bidders:
            bidders_str = conv_bidders_to_str(lot.bidders[::-1])
            lot.create_text("lot number", bidders_str)
        else:
            lot.create_text()

    if lot_category == 'sold_lots':
        for index, bidder in enumerate(lot.bidders[::-1]):
            lot.text += (
                f'{index + 1} место:\n{bidder["first_name"]}, '
                f'{bidder["last_name"]}, {bidder["user_name"]}, '
                f'{bidder["id"]}, {bidder["price"]} ₽\n\n'
            )

    return lot.text


def remove_exhibited_lot(lot_number):
    for lot in AuctionLot.exhibited_lots:
        if lot_number == lot.number:
            AuctionLot.exhibited_lots.remove(lot)


async def put_a_lot_up_for_auction(lot_args, lot_number, chat_id, message_id):
    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row('ready_lots', 'lot_number', lot_number)
        data_base.save_row('raffled_lots', *lot_data)
        data_base.remove_some_rows('ready_lots', 'lot_number', lot_number)

    lot = AuctionLot(*lot_args)

    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id
    )

    photo = await bot.send_photo(
        CHAT_ID,
        lot.main_photo,
        caption=lot.create_text(),
        reply_markup=make_auction_keyboard(lot_number)
    )

    with LiteBase('data_base.db') as data_base:
        data_base.update_column('raffled_lots', 'end_time', lot.end_time, 'lot_number', lot_number)
        data_base.update_column('raffled_lots', 'message_id', photo.message_id, 'lot_number', lot_number)

    AuctionLot.exhibited_lots.append(lot)

    return lot, photo


async def close_auction(lot, photo, lot_number):
    lot.applicant_id = None

    with LiteBase('data_base.db') as data_base:
        data_base.update_column('raffled_lots', 'end_time', None, 'lot_number', lot_number)
        data_base.update_column('raffled_lots', 'message_id', None, 'lot_number', lot_number)
        lot_data = data_base.load_row('raffled_lots', 'lot_number', lot_number)
        data_base.remove_some_rows('raffled_lots', 'lot_number', lot_number)

        if lot.bidders:
            lot.winner = lot.bidders[-1]
            lot.create_text("lot number", conv_winner_to_str(lot.winner))

            data_base.save_row('sold_lots', *lot_data)

            data_base.save_row(
                'winner', lot_number, lot.winner["first_name"],
                lot.winner["last_name"], lot.winner["user_name"],
                lot.winner["id"], lot.winner["price"]
            )
        else:
            data_base.save_row('ready_lots', *lot_data)
            data_base.update_column('ready_lots', 'current_price', None, 'lot_number', lot_number)

        await photo.edit_caption(lot.text)

        remove_exhibited_lot(lot_number)


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
    lot_category = callback.data.split()[1]
    lot_number = int(callback.data.split()[2])

    lot_args = get_lot_args(lot_category, lot_number)
    lot = AuctionLot(*lot_args)

    await bot.send_photo(
        callback.message.chat.id,
        photo=lot.main_photo,
        caption=compose_lot_text(lot, lot_category),
        reply_markup=make_lot_management_kb(lot_category, lot_number)
    )


# @dp.callback_query_handler(Text(startswith='to_ready'))
async def move_to_ready(callback: types.CallbackQuery):
    lot_category = callback.data.split()[1]
    lot_number = int(callback.data.split()[2])

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )

    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row(lot_category, 'lot_number', lot_number)

        if lot_data:
            data_base.save_row('ready_lots', *lot_data)

            if lot_category == 'raffled_lots':
                message_id = data_base.load_column(lot_category, 'message_id', 'lot_number', lot_number)
                await bot.delete_message(CHAT_ID, message_id)

            data_base.update_column('ready_lots', 'end_time', None, 'lot_number', lot_number)
            data_base.update_column('ready_lots', 'message_id', None, 'lot_number', lot_number)
            data_base.update_column('ready_lots', 'current_price', None, 'lot_number', lot_number)

            data_base.remove_some_rows(lot_category, 'lot_number', lot_number)
            data_base.remove_some_rows('bidders', 'lot_number', lot_number)
            data_base.remove_some_rows('winner', 'lot_number', lot_number)

    remove_exhibited_lot(lot_number)


# @dp.callback_query_handler(Text(startswith='remove'))
async def remove_lot(callback: types.CallbackQuery):
    lot_category = callback.data.split()[1]
    lot_number = int(callback.data.split()[2])

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )

    with LiteBase('data_base.db') as data_base:
        if lot_category == 'raffled_lots':
            message_id = data_base.load_column(lot_category, 'message_id', 'lot_number', lot_number)
            await bot.delete_message(CHAT_ID, message_id)

        data_base.remove_some_rows(lot_category, 'lot_number', lot_number)
        data_base.remove_some_rows('winner', 'lot_number', lot_number)
        data_base.remove_some_rows('bidders', 'lot_number', lot_number)

    remove_exhibited_lot(lot_number)


# @dp.callback_query_handler(Text(startswith='for_auction'))
async def send_lot_for_auction(callback: types.CallbackQuery):
    lot_category = callback.data.split()[1]
    lot_number = int(callback.data.split()[2])
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    lot_args = get_lot_args(lot_category, lot_number)

    if lot_args:
        lot, photo = await put_a_lot_up_for_auction(lot_args, lot_number, chat_id, message_id)

        await lot.start_lot_timer(20)

        if lot in AuctionLot.exhibited_lots:
            await close_auction(lot, photo, lot_number)


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
