from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from my_lib.emojis import stopwatch_emoji, warning_emoji, photo_emoji
from create_bot import BOT_NAME


def make_auction_keyboard(lot_number):
    make_bid_btn = InlineKeyboardButton(
        text='+2000',
        callback_data=f'+2000 {lot_number}'
    )

    detail_info = InlineKeyboardButton(
        text=f'{photo_emoji} Больше информации и фото',
        url=f'https://t.me/{BOT_NAME}?start={lot_number}'
    )

    time_left_btn = InlineKeyboardButton(
        text=stopwatch_emoji,
        callback_data=f'time_left {lot_number}'
    )

    warning_btn = InlineKeyboardButton(
        text=warning_emoji,
        callback_data='warning'
    )

    auction_keyboard = InlineKeyboardMarkup()
    auction_keyboard.add(detail_info).add(make_bid_btn).row(time_left_btn, warning_btn)

    return auction_keyboard


def make_confirm_keyboard(lot_number):
    no_btn = InlineKeyboardButton(
        text='НЕТ',
        callback_data=f'no {lot_number}'
    )

    yes_btn = InlineKeyboardButton(
        text='ДА',
        callback_data=f'yes {lot_number}'
    )

    confirm_keyboard = InlineKeyboardMarkup()
    confirm_keyboard.row(no_btn, yes_btn)

    return confirm_keyboard
