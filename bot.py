from create_bot import dp, data_base
from handlers import client, admin, states, other
from aiogram import executor


async def on_startup(_):
    print('Бот вышел в онлайн!')


def main():
    table_columns = (
        'lot_number', 'auction_time', 'price', 'main_photo',
        'other_photos', 'videos', 'description', 'end_time', 'message_id'
    )

    data_base.connect()
    data_base.create_table('ready_lots', *table_columns)
    data_base.create_table('raffled_lots', *table_columns)
    data_base.create_table('sold_lots', *table_columns)
    data_base.close()

    client.register_client_handlers(dp)
    admin.register_admin_handlers(dp)
    states.register_states_handlers(dp)
    other.register_other_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
