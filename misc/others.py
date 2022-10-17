from create_bot import bot, CHAT_ID
from my_lib.lite_base import LiteBase
from my_lib.emojis import gold_medal_emoji, silver_medal_emoji, bronze_medal_emoji
from keyboards.admin_kb import make_more_lot_info_kb
from keyboards.client_kb import make_auction_keyboard
from misc.auction_lot import AuctionLot


def get_data_for_lot_management(callback):
    lot_category = callback.data.split()[1]
    lot_number = int(callback.data.split()[2])
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    return lot_category, lot_number, chat_id, message_id


def get_lot_args(lot_category, lot_number):
    lot_args = None
    bidders = []
    winner = None

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

    if winner_data:
        winner = winner_data[1:]

        winner = {
            "first_name": winner[0],
            "last_name": winner[1],
            "user_name": winner[2],
            "id": winner[3],
            "price": winner[4]
        }

    if lot_data:
        lot_args = list(lot_data)
        addit_media = lot_data[5].split(',')

        lot_args[5] = addit_media
        lot_args.insert(7, bidders)
        lot_args.insert(8, winner)

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


def conv_winner_to_str(winner: dict):
    return f'{gold_medal_emoji} {winner["price"]} ₽ {winner["first_name"][:3]}**'


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


async def delete_raffled_lot_message(data_base, lot_category, lot_number):
    if lot_category == 'raffled_lots':
        message_id = data_base.load_column(lot_category, 'message_id', 'lot_number', lot_number)

        try:
            await bot.delete_message(CHAT_ID, message_id)

        except Exception as error:
            print('error:', error)


def update_lot_from_database(data_base, lot_category, lot_number):
    data_base.update_column(lot_category, 'end_time', None, 'lot_number', lot_number)
    data_base.update_column(lot_category, 'message_id', None, 'lot_number', lot_number)
    data_base.update_column(lot_category, 'current_price', None, 'lot_number', lot_number)


def remove_lot_from_database(data_base, lot_category, lot_number):
    data_base.remove_some_rows(lot_category, 'lot_number', lot_number)
    data_base.remove_some_rows('bidders', 'lot_number', lot_number)
    data_base.remove_some_rows('winner', 'lot_number', lot_number)


def remove_lot_from_memory(lot_number):
    for lot in AuctionLot.exhibited_lots:
        if lot_number == lot.number:
            AuctionLot.exhibited_lots.remove(lot)


async def put_a_lot_up_for_auction(lot, chat_id, message_id):
    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row('ready_lots', 'lot_number', lot.number)
        data_base.save_row('raffled_lots', *lot_data)
        data_base.remove_some_rows('ready_lots', 'lot_number', lot.number)

    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id
    )

    photo = await bot.send_photo(
        CHAT_ID,
        lot.main_photo,
        caption=lot.create_text(),
        reply_markup=make_auction_keyboard(lot.number)
    )

    photo_id = photo.message_id

    with LiteBase('data_base.db') as data_base:
        data_base.update_column('raffled_lots', 'end_time', lot.end_time, 'lot_number', lot.number)
        data_base.update_column('raffled_lots', 'message_id', photo.message_id, 'lot_number', lot.number)

    AuctionLot.exhibited_lots.append(lot)

    return photo_id


async def complete_auction_lot(lot, message_id):
    lot.applicant_id = None

    with LiteBase('data_base.db') as data_base:
        lot_data = data_base.load_row('raffled_lots', 'lot_number', lot.number)
        data_base.remove_some_rows('raffled_lots', 'lot_number', lot.number)

        if lot.bidders:
            lot.winner = lot.bidders[-1]
            lot.create_text("lot number", conv_winner_to_str(lot.winner))

            data_base.save_row('sold_lots', *lot_data)

            data_base.save_row(
                'winner', lot.number, lot.winner["first_name"],
                lot.winner["last_name"], lot.winner["user_name"],
                lot.winner["id"], lot.winner["price"]
            )
        else:
            data_base.save_row('ready_lots', *lot_data)
            update_lot_from_database(data_base, 'ready_lots', lot.number)

    await bot.edit_message_caption(
        chat_id=CHAT_ID,
        message_id=message_id,
        caption=lot.text,
    )

    remove_lot_from_memory(lot.number)
