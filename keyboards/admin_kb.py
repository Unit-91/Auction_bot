from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.types.web_app_info import WebAppInfo


def make_admin_kb():
    # load_lot_btn = KeyboardButton(text='/Загрузить_лот', web_app=WebAppInfo(url=''))
    load_lot_btn = KeyboardButton('/Загрузить_лот')
    show_lots_btn = KeyboardButton('/Показать_лоты')

    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    admin_keyboard.row(load_lot_btn, show_lots_btn)

    return admin_keyboard


def make_cancel_kb():
    load_cancel_btn = KeyboardButton('/Отмена')
    empty_btn = KeyboardButton(' ')

    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.row(empty_btn, load_cancel_btn, empty_btn)

    return cancel_keyboard


def make_stop_kb():
    stop_btn = KeyboardButton('/Хватит')
    empty_btn = KeyboardButton(' ')
    load_cancel_btn = KeyboardButton('/Отмена')

    stop_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    stop_keyboard.row(empty_btn, stop_btn, empty_btn).add(load_cancel_btn)

    return stop_keyboard


def make_categories_kb():
    ready_lots_btn = KeyboardButton('/Готовые_к_аукциону')
    raffled_lots_btn = KeyboardButton('/Выставленные')
    sold_lots_btn = KeyboardButton('/Проданные')
    back_btn = KeyboardButton('/Назад')

    categories_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    categories_keyboard.row(ready_lots_btn, raffled_lots_btn, sold_lots_btn).add(back_btn)

    return categories_keyboard


def make_more_lot_info_kb(lot_category, lot_number):
    lot_num_btn = InlineKeyboardButton(
        text='Подробнее',
        callback_data=f'more {lot_category} {lot_number}'
    )

    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(lot_num_btn)

    return inline_keyboard


def make_lot_management_kb(lot_category, lot_number):
    for_auction_btn = InlineKeyboardButton(
        text='На аукцион',
        callback_data=f'for_auction {lot_number}'
    )

    to_ready_btn = InlineKeyboardButton(
        text='В готовые',
        callback_data=f'to_ready {lot_number}'
    )

    remove_btn = InlineKeyboardButton(
        text='Удалить',
        callback_data=f'remove {lot_category} {lot_number}'
    )

    lot_management_keyboard = InlineKeyboardMarkup()

    if lot_category == 'ready_lots':
        lot_management_keyboard.row(for_auction_btn, remove_btn)

    elif lot_category == 'sold_lots':
        lot_management_keyboard.row(to_ready_btn, remove_btn)

    else:
        lot_management_keyboard.add(remove_btn)

    return lot_management_keyboard
