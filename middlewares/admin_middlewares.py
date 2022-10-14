from create_bot import bot, CHAT_ID
import asyncio
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from handlers import states


async def remove_admin_id(admin_id, seconds):
    await asyncio.sleep(seconds)
    states.FSMAdmin.admin_ids.remove(admin_id)


# if not ('-100' in str(Chat_id)):
class GetAdminsMiddleWare(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.chat.id != CHAT_ID:

            if message.text != '/start':

                if message.from_user.id not in states.FSMAdmin.admin_ids:
                    admins = await bot.get_chat_administrators(CHAT_ID)

                    for item in admins:
                        if message.from_user.id == item.user.id:
                            states.FSMAdmin.admin_ids.append(item.user.id)
                            task = asyncio.create_task(remove_admin_id(item.user.id, 10))
                            asyncio.gather(task)
