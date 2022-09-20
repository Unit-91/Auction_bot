from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_admin_keyboard():
    load_lot_btn = KeyboardButton('/Загрузить_лот')
    show_lots_btn = KeyboardButton('/Показать_лоты')

    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    admin_keyboard.row(load_lot_btn, show_lots_btn)

    return admin_keyboard


def make_cancel_keyboard():
    load_cancel_btn = KeyboardButton('/Отмена')
    empty_btn = KeyboardButton(' ')

    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.row(empty_btn, load_cancel_btn, empty_btn)

    return cancel_keyboard
