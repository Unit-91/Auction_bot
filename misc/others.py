from create_bot import bot
from my_lib.lite_base import LiteBase
from my_lib.emojis import gold_medal_emoji, silver_medal_emoji, bronze_medal_emoji
from keyboards.admin_kb import make_more_lot_info_keyboard


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
                "price": bidder[4]
            }

            for bidder in bidders
        ]

        winner = winner_data[1:]

        winner = {
            "first_name": winner[0],
            "last_name": winner[1],
            "user_name": winner[2],
            "id": winner[3],
            "price": winner[4]
        }
    else:
        bidders = []
        winner = {}

    lot_args = list(lot_data)

    lot_args.insert(8, bidders)
    lot_args.insert(9, winner)

    return lot_args


def conv_bidders_to_str(bidders_list):
    bidders_str = ''
    emojis = [gold_medal_emoji, silver_medal_emoji, bronze_medal_emoji]

    for index, bidder in enumerate(bidders_list):
        if index < 3:
            bidders_str += f'{emojis[index]} {bidder["price"]} ₽ {bidder["first_name"][:3]}**\n'
        else:
            break

    return bidders_str[:-1]


def compose_lot_text(lot, lot_category):
    if lot_category == 'ready_lots':
        lot.create_text()

    if lot_category == 'reffled_lots':
        bidders_str = conv_bidders_to_str(lot.bidders[::-1])
        lot.create_text("lot number", bidders_str)

    if lot_category == 'sold_lots':
        for index, bidder in enumerate(lot.bidders[::-1]):
            lot.text += (
                f'{index + 1} место:\n{bidder["first_name"]}, '
                f'{bidder["last_name"]}, {bidder["user_name"]}, '
                f'{bidder["id"]}, {bidder["price"]} ₽\n\n'
            )

    return lot.text
