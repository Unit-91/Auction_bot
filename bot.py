from create_bot import dp, bot, CHAT_ID, BOT_CHAT_ID
from handlers import client, admin, states, other
from aiogram import executor, types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class GetAdminsMiddleWare(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.chat.id == BOT_CHAT_ID and message.text != '/start':
            admins = await bot.get_chat_administrators(CHAT_ID)

            states.FSMAdmin.admin_ids.clear()

            for item in admins:
                states.FSMAdmin.admin_ids.append(item.user.id)


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
