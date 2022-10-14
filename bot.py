from create_bot import dp
from handlers import client, admin, states, other
from aiogram import executor
from middlewares.admin_middlewares import GetAdminsMiddleWare


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
