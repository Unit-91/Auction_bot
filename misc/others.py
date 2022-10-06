from create_bot import bot
from my_lib.lite_base import LiteBase
from keyboards.admin_kb import make_more_lot_info_keyboard, make_lot_management_keyboard
from misc.auction_lot import AuctionLot


async def show_lot_numbers(message, lot_category):
    with LiteBase('data_base.db') as data_base:
        lst = data_base.load_all_columns('lot_number', lot_category)

    if lst:
        for lot_number in lst:
            await bot.send_message(
                message.from_user.id,
                text=f'Лот № {lot_number}',
                reply_markup=make_more_lot_info_keyboard(lot_category, lot_number)
            )
    else:
        await message.answer('В этой категории нет лотов')


def get_lot_args(lot_category, lot_number):
    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row(lot_category, 'lot_number', lot_number)
        bidders_data = data_base.load_some_rows('bidders', 'lot_number', str(lot_number))
        winner_data = data_base.load_row('winner', 'lot_number', str(lot_number))
        # Убрать str()

    if bidders_data:
        bidders = [bidder[1:] for bidder in bidders_data]

        bidders = [
            {
                "first_name": bidder[0],
                "last_name": bidder[1],
                "user_name": bidder[2],
                "id": bidder[3],
                "start_price": bidder[4]
            }

            for bidder in bidders
        ]

        winner = winner_data[1:]

        winner = {
            "first_name": winner[0],
            "last_name": winner[1],
            "user_name": winner[2],
            "id": winner[3],
            "start_price": winner[4]
        }
    else:
        bidders = []
        winner = {}

    lot_args = list(lot_data)

    lot_args.insert(7, bidders)
    lot_args.insert(8, winner)

    return lot_args


async def show_lot(chat_id, lot_category, lot_number):
    lot_args = get_lot_args(lot_category, lot_number)

    lot = AuctionLot(*lot_args)

    await bot.send_photo(
        chat_id,
        photo=lot.main_photo,
        caption=lot.text,
        reply_markup=make_lot_management_keyboard(lot_category, lot_number)
    )
