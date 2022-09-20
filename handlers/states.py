from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from create_bot import bot, data_base
from keyboards.admin_kb import make_admin_keyboard


class FSMAdmin(StatesGroup):
    lot_number = State()
    auction_time = State()
    price = State()
    main_photo = State()
    other_photos = State()
    videos = State()
    full_description = State()


# @dp.message_handler(commands=['admin'], is_chat_admin=True)
async def send_admin_keyboard(message: types.Message):
    FSMAdmin.admin_id = message.from_user.id

    await bot.send_message(
        FSMAdmin.admin_id,
        'Чего надо хозяин?',
        reply_markup=make_admin_keyboard()
    )
    await message.delete()


def register_states_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_keyboard, commands=['admin'], is_chat_admin=True)
