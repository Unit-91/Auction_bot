from time import time
from my_lib.different_funcs import get_hours_ending, conv_to_pref_format
from my_lib.emojis import exclam_emoji, fire_emoji, push_pin_emoji, money_bag_emoji
from asyncio import sleep


class AuctionLot():
    exhibited_lots = []

    def __init__(
        self, lot_number, auction_time, start_price, current_price, main_photo,
        addit_media, description, bidders, winner, end_time, message_id
    ):
        self.number = lot_number
        self.auction_time = auction_time
        self.start_price = start_price

        if current_price:
            self.current_price = current_price
        else:
            self.current_price = start_price

        self.main_photo = main_photo
        self.addit_media = addit_media
        self.description = description
        self.bidders = bidders
        self.winner = winner
        self.end_time = end_time if end_time else int(time() + (self.auction_time * 3600))
        self.message_id = message_id

        self.pressing_sequence_num = 0
        self.applicant_id = None

        self.strings = {
            "auction duration": (
                f'{exclam_emoji} Продолжительность аукциона - '
                f'{self.auction_time} {get_hours_ending(self.auction_time)} {exclam_emoji}'
            ),
            "start price": f'{fire_emoji} СТАРТ {self.start_price} ₽ {fire_emoji}\n',
            "lot number": f'{push_pin_emoji} Лот № {self.number}',
            "current price": f'\n{money_bag_emoji} ТЕКУЩАЯ ЦЕНА: {self.current_price} ₽'
        }

        self.text = ''

    def create_text(self, position=None, text_insert=None):
        self.text = ''

        for key, value in self.strings.items():
            self.text += f'{value}\n'

            if key == position:
                self.text += f'{text_insert}\n'

        return self.text

    async def start_timer(self, seconds):
        await sleep(seconds)

    async def start_confirm_timer(self, seconds):
        await sleep(seconds)

    def get_time_left(self):
        time_left = conv_to_pref_format(self.end_time - int(time()))

        return time_left
