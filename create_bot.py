from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv
from my_lib.lite_base import LiteBase

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

CHAT_ID = int(os.getenv('CHAT_ID'))
CHAT_OWNER_ID = int(os.getenv('CHAT_OWNER_ID'))
BOT_NAME = os.getenv('BOT_NAME')

data_base = LiteBase('data_base.db')


def create_data_base_tables():
    lot_table_columns = (
        'lot_number', 'auction_time', 'price', 'current_price', 'main_photo',
        'addit_media', 'description', 'end_time', 'message_id'
    )

    bidders_and_winner_columns = (
        "lot_number", "first_name",
        "last_name", "user_name", "id", "price"
    )

    with LiteBase('data_base.db') as data_base:
        data_base.create_table('ready_lots', *lot_table_columns)
        data_base.create_table('raffled_lots', *lot_table_columns)
        data_base.create_table('sold_lots', *lot_table_columns)

        data_base.create_table('bidders', None, *bidders_and_winner_columns)
        data_base.create_table('winner', *bidders_and_winner_columns)


create_data_base_tables()
