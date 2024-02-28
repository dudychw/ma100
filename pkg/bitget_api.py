import datetime

from pybitget import Client
import pandas as pd
from config.config import Config
from pkg.logger import Logger


class BitGetApi:
    def __init__(self):
        self.config = Config()
        self.iClient = Client(self.config.api_key, self.config.api_secret, self.config.api_passphrase,
                              use_server_time=False)
        self.logg = Logger()

    def get_quantity(self):
        try:
            available = float(
                self.iClient.mix_get_account(symbol=self.config.symbol_basic_usdt_bg,
                                             marginCoin='USDT')['data']['available'])
            price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
            return str(int(available / price_now) - 1)
        except Exception as err:
            self.logg.logger('QUANTITY_ERROR', f'text: {err}')

    def get_order(self, symbol, side, quantity=None, orderType='market'):
        try:
            if 'open' in side:
                # quantity = min([self.get_quantity() for _ in range(3)])
                quantity = self.get_quantity()
            order_id = self.iClient.mix_place_order(symbol=symbol, marginCoin='USDT', size=quantity,
                                                    side=side, orderType=orderType)['data']['orderId']
            price_order = self.iClient.mix_get_order_details(symbol=self.config.symbol_basic_usdt_bg,
                                                             orderId=order_id)['data']['price']
            return price_order, quantity
        except Exception as err:
            self.logg.logger('ORDER_ERROR', f'text: {err}')

    def get_simple_profit(self, side, price_open, y):
        profit = None
        if side == 'buy':
            profit = ((y - price_open) / price_open) * 100
        elif side == 'sell':
            profit = ((price_open - y) / price_open) * 100
        return round(profit, 3)

    def bg_get_profit(self, price_open, side, ma100=False, yi=None):
        try:
            if ma100:
                return self.get_simple_profit(side, price_open, yi)
            else:
                price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
                return self.get_simple_profit(side, price_open, price_now), price_now
        except Exception as err:
            self.logg.logger('GET_PROFIT_ERROR', f'text: {err}')
