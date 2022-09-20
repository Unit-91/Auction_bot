from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv
from my_lib.lite_base import LiteBase

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
data_base = LiteBase('data_base.db')

CHAT_ID = int(os.getenv('CHAT_ID'))
BOT_NAME = os.getenv('BOT_NAME')
