# import asyncio
import time
from my_lib.emoji import exclam_emoji, fire_emoji, push_pin_emoji, money_bag_emoji


def form_hourse_ending(hours):
    ending = ''
    hours = hours % 20

    if hours == 1:
        ending = 'час'

    elif hours > 1 and hours < 5:
        ending = 'часа'

    else:
        ending = 'часов'

    return ending


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

        ending = form_hourse_ending(self.auction_time)

        self.strings = {
            "auction duration": (
                f'{exclam_emoji} Продолжительность аукциона - '
                f'{self.auction_time} {ending} {exclam_emoji}'
            ),
            "start price": f'{fire_emoji} СТАРТ {self.price} ₽ {fire_emoji}',
            "lot number": f'{push_pin_emoji} Лот № {self.lot_num}',
            "current price": f'{money_bag_emoji} ТЕКУЩАЯ ЦЕНА: {self.current_price} ₽'
        }

        self.text = None
