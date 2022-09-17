from misc.auction_lot import AuctionLot
# from aiogram import executor
# from create_bot import dp
# from handlers import client, admin, other


# async def on_startup(_):
#     print('Бот вышел в онлайн!')


# def main():
#     client.register_client_handlers(dp)
#     admin.register_admin_handlers(dp)
#     other.register_other_handlers(dp)

#     executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


# if __name__ == '__main__':
#     main()

lot = AuctionLot(1, 2, 3, 4, 'FAF', 'REW', 'CVC', 'Fadg', None, None, 234324332, 43243232)
print(lot.strings["auction duration"])
