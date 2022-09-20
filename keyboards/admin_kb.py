from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_admin_keyboard():
    load_lot_btn = KeyboardButton('/Загрузить_лот')
    show_lots_btn = KeyboardButton('/Показать_лоты')

    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    admin_keyboard.row(load_lot_btn, show_lots_btn)

    return admin_keyboard
