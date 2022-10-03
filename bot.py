from create_bot import dp, bot, CHAT_ID
from handlers import client, admin, states, other
from aiogram import executor, types
from aiogram.dispatcher.middlewares import BaseMiddleware
import asyncio


async def remove_id(admin_id, seconds):
    await asyncio.sleep(seconds)
    states.FSMAdmin.admin_ids.remove(admin_id)
    print(states.FSMAdmin.admin_ids)


class GetAdminsMiddleWare(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.chat.id != CHAT_ID:

            if message.text != '/start':

                if message.from_user.id not in states.FSMAdmin.admin_ids:
                    admins = await bot.get_chat_administrators(CHAT_ID)

                    for item in admins:

                        if message.from_user.id == item.user.id:
                            states.FSMAdmin.admin_ids.append(item.user.id)
                            print(states.FSMAdmin.admin_ids)
                            task = asyncio.create_task(remove_id(item.user.id, 20))
                            asyncio.gather(task)

        # if not ('-100' in str(Chat_id)):


async def on_startup(_):
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
