from my_lib.lite_base import LiteBase
from my_lib.emojis import gold_medal_emoji, silver_medal_emoji, bronze_medal_emoji


def get_lot_args(lot_category, lot_number):
    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row(lot_category, 'lot_number', lot_number)
        bidders_data = data_base.load_some_rows('bidders', 'lot_number', lot_number)
        winner_data = data_base.load_row('winner', 'lot_number', lot_number)

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


def conv_bidders_to_str(bidders: list):
    bidders_str = ''
    emojis = [gold_medal_emoji, silver_medal_emoji, bronze_medal_emoji]

    for index, bidder in enumerate(bidders):
        if index < 3:
            bidders_str += f'{emojis[index]} {bidder["price"]} ₽ {bidder["first_name"][:3]}**\n'
        else:
            break

    return bidders_str[:-1]


def conv_winner_to_str(winner: tuple):
    pass
