from create_bot import dp, bot, CHAT_ID
from handlers import client, admin, states, other
from aiogram import executor
from middlewares.admin_middlewares import GetAdminsMiddleWare
from my_lib.lite_base import LiteBase
from misc.others import get_lot_args, conv_bidders_to_str, complete_auction_lot
from misc.auction_lot import AuctionLot
from time import time
from keyboards.client_kb import make_auction_keyboard
import asyncio


async def restarting_the_bot(lot_args):
    lot = AuctionLot(*lot_args)

    if lot.end_time > int(time()):
        if lot.bidders:
            lot.create_text("lot number", conv_bidders_to_str(lot.bidders[::-1]))
        else:
            lot.create_text()

        AuctionLot.exhibited_lots.append(lot)

        try:
            await bot.edit_message_caption(
                chat_id=CHAT_ID,
                message_id=lot.message_id,
                caption=lot.text,
                reply_markup=make_auction_keyboard(lot.number)
            )
            print('Возобновление работы')

        except Exception:
            print('Возобновление работы')

        await lot.start_timer(20)

        await complete_auction_lot(lot, lot.message_id)

    else:
        await complete_auction_lot(lot, lot.message_id)


async def on_startup(_):
    with LiteBase('data_base.db') as data_base:
        raffled_lot_numbers = data_base.load_all_columns('lot_number', 'raffled_lots')

    for number in raffled_lot_numbers:
        lot_args = get_lot_args('raffled_lots', number)

        task = asyncio.create_task(restarting_the_bot(lot_args))
        asyncio.gather(task)

    print('Бот вышел в онлайн!')


def main():
    client.register_client_handlers(dp)
    admin.register_admin_handlers(dp)
    states.register_states_handlers(dp)
    other.register_other_handlers(dp)

    dp.middleware.setup(GetAdminsMiddleWare())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
