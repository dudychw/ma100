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

    def get_quantity(self, price=None):
        try:
            available = float(
                self.iClient.mix_get_account(symbol=self.config.symbol_basic_usdt_bg,
                                             marginCoin='USDT')['data']['available'])
            if price is None:
                price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
                return str(int(available / price_now) - 1)
            else:
                return str(int(available / price) - 1)
        except Exception as err:
            self.logg.logger('QUANTITY_ERROR', f'text: {err}')

    def get_order(self, symbol, side, quantity=None, price=None):
        try:
            if 'open' in side:
                if price is None:
                    quantity = self.get_quantity()
                else:
                    quantity = self.get_quantity(price)

            if price is None:
                order_id = self.iClient.mix_place_order(symbol=symbol, marginCoin='USDT', size=quantity,
                                                        side=side, orderType='market')['data']['orderId']
                price_order = self.iClient.mix_get_order_details(symbol=self.config.symbol_basic_usdt_bg,
                                                                 orderId=order_id)['data']['price']
                return price_order, quantity
            else:
                order_id = self.iClient.mix_place_order(symbol=symbol, marginCoin='USDT', size=quantity,
                                                        side=side, orderType='limit', price=price)['data']['orderId']
                price_order = self.iClient.mix_get_order_details(symbol=self.config.symbol_basic_usdt_bg,
                                                                 orderId=order_id)['data']['price']
                return order_id, price_order, quantity

        except Exception as err:
            self.logg.logger('ORDER_ERROR', f'text: {err}')

    def cancel_order(self, symbol, order_id):
        self.iClient.mix_cancel_order(symbol=symbol, marginCoin='USDT', orderId=order_id)

    def get_simple_profit(self, side, price_open, y):
        if side == 'long':
            return round(((y - price_open) / price_open) * 100, 3)
        elif side == 'short':
            return round(((price_open - y) / price_open) * 100, 3)

    def bg_get_profit(self, price_open, side, ma100=False, yi=None):
        try:
            if ma100:
                return self.get_simple_profit(side, price_open, yi)
            else:
                price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
                return self.get_simple_profit(side, price_open, price_now), price_now
        except Exception as err:
            self.logg.logger('GET_PROFIT_ERROR', f'text: {err}')

    def get_status(self, symbol, order_id):
        return self.iClient.mix_get_order_details(symbol=symbol, orderId=order_id)['data']['state'] == 'filled'


