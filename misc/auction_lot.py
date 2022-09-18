import asyncio
import time
from my_lib.different_funcs import get_hours_ending, conv_to_pref_format
from my_lib.emojis import exclam_emoji, fire_emoji, push_pin_emoji, money_bag_emoji


class AuctionLot():
    def __init__(
        self, lot_num, auction_time, price, current_price, main_photo,
        other_photos, videos, description, bidders, winner, end_time, message_id
    ):
        self.lot_num = lot_num
        self.auction_time = auction_time
        self.price = price
        self.current_price = current_price
        self.main_photo = main_photo
        self.other_photos = other_photos
        self.videos = videos
        self.description = description
        self.bidders = bidders
        self.winner = winner
        self.end_time = end_time if end_time else int(time.time() + (self.auction_time * 3600))
        self.message_id = message_id

        self.pressing_sequence_num = 0
        self.applicant_id = None

        self.strings = {
            "auction duration": (
                f'{exclam_emoji} Продолжительность аукциона - '
                f'{self.auction_time} {get_hours_ending(self.auction_time)} {exclam_emoji}'
            ),
            "start price": f'{fire_emoji} СТАРТ {self.price} ₽ {fire_emoji}',
            "lot number": f'{push_pin_emoji} Лот № {self.lot_num}',
            "current price": f'{money_bag_emoji} ТЕКУЩАЯ ЦЕНА: {self.current_price} ₽'
        }

        self.text = (
            f'{self.strings["auction duration"]}\n'
            f'{self.strings["start price"]}\n\n'
            f'{self.strings["lot number"]}\n\n'
            f'{self.strings["current price"]}'
        )

    async def start_lot_timer(self, seconds):
        await asyncio.sleep(seconds)

    async def start_confirm_timer(self, seconds):
        await asyncio.sleep(seconds)

    def get_time_left(self):
        time_left = conv_to_pref_format(self.end_time - int(time.time()))

        return time_left
