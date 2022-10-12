from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from misc.auction_lot import AuctionLot
from keyboards.client_kb import make_confirm_keyboard, make_auction_keyboard


# @dp.callback_query_handler(Text(startswith='+2000'))
async def make_bid(callback: types.CallbackQuery):
    lot_number = int(callback.data.split()[1])
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name

    for lot in AuctionLot.exhibited_lots:

        if lot_number == lot.number:

            if not lot.bidders or lot.bidders[-1]["id"] != user_id:
                await callback.message.edit_caption(
                    caption=f'{lot.text}\n\n{first_name} вы подтверждаете ставку?',
                    reply_markup=make_confirm_keyboard(lot_number)
                )

                lot.applicant_id = user_id
                lot.pressing_sequence_num += 1

                pressing_sequence_num = lot.pressing_sequence_num

                await lot.start_confirm_timer(20)

                if pressing_sequence_num == lot.pressing_sequence_num and lot.applicant_id is not None:
                    await callback.message.edit_caption(
                        caption=lot.text,
                        reply_markup=make_auction_keyboard(lot_number)
                    )

            elif lot.bidders[-1]["id"] == user_id:
                await callback.answer('Подождите пока вашу ставку перебьют', show_alert=True)


# @dp.callback_query_handler(Text(startswith='time_left'))
async def show_remaining_time(callback: types.CallbackQuery):
    lot_number = int(callback.data.split()[1])
    user_id = callback.from_user.id

    for lot in AuctionLot.exhibited_lots:

        if lot_number == lot.number:
            await callback.answer(lot.get_time_left())


# @dp.callback_query_handler(text='warning')
async def show_warning(callback: types.CallbackQuery):
    await callback.answer(
        'Если победитель в течение одного часа не подтверждает свое желание\
        приобрести лот, он передается следующему участнику',
        show_alert=True
    )


# @dp.callback_query_handler(Text(startswith='no'))
async def cancel_the_bid(callback: types.CallbackQuery):
    lot_number = int(callback.data.split()[1])
    user_id = callback.from_user.id

    for lot in AuctionLot.exhibited_lots:

        if lot_number == lot.number:

            if lot.applicant_id == user_id:
                lot.applicant_id = None

                await callback.message.edit_caption(
                    caption=lot.text,
                    reply_markup=make_auction_keyboard(lot_number)
                )
            else:
                await callback.answer(
                    'Подождите пока другой игрок закончит совершение ставки',
                    show_alert=True
                )


def register_client_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(make_bid, Text(startswith='+2000'))
    dp.register_callback_query_handler(show_remaining_time, Text(startswith='time_left'))
    dp.register_callback_query_handler(show_warning, text='warning')
    dp.register_callback_query_handler(cancel_the_bid, Text(startswith='no'))
