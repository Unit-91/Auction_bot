from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from handlers.states import FSMAdmin
from keyboards.admin_kb import make_categories_keyboard, make_admin_keyboard, make_lot_management_keyboard
from misc.others import show_lot_numbers, get_lot_args, compose_lot_text
from misc.auction_lot import AuctionLot


# @dp.message_handler(commands=['Показать_лоты'])
async def show_lot_categories(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Выбери категорию лотов',
            reply_markup=make_categories_keyboard()
        )


# @dp.message_handler(commands=['Назад'])
async def go_back(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Чего надо хозяин?',
            reply_markup=make_admin_keyboard()
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

    lot.text = compose_lot_text(lot, lot_category)

    await bot.send_photo(
        callback.message.chat.id,
        photo=lot.main_photo,
        caption=lot.text,
        reply_markup=make_lot_management_keyboard(lot_category, lot_number)
    )


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(show_lot_categories, commands=['Показать_лоты'])
    dp.register_message_handler(go_back, commands=['Назад'])
    dp.register_message_handler(show_ready_lots, commands=['Готовые_к_аукциону'])
    dp.register_message_handler(show_raffled_lots, commands=['Выставленные'])
    dp.register_message_handler(show_sold_lots, commands=['Проданные'])
    dp.register_callback_query_handler(show_more_lot_info, Text(startswith='more'))
