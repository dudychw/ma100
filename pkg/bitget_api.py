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

    def df_candles_time(self, symbol, time_start, time_end):
        try:
            # get candles data
            candles = self.iClient.mix_get_candles(symbol=symbol,
                                                   granularity=self.config.period_str,
                                                   startTime=time_start,
                                                   endTime=time_end)

            return pd.DataFrame({
                'ts': [float(el[0]) for el in candles],
                'open': [float(el[1]) for el in candles],
                'high': [float(el[2]) for el in candles],
                'low': [float(el[3]) for el in candles],
                'close': [float(el[4]) for el in candles]
            })
        except Exception as err:
            self.logg.logger('GET_CANDLES_DF_ERROR', f'text: {err}')

    def df_candles(self, symbol, n):
        try:
            # get candles data
            time_end = datetime.datetime.now()
            time_start = (time_end - datetime.timedelta(minutes=n * self.config.period_int))
            candles = self.iClient.mix_get_candles(symbol=symbol,
                                                   granularity=self.config.period_str,
                                                   startTime=int(time_start.timestamp()) * 1000,
                                                   endTime=int(time_end.timestamp()) * 1000, limit=str(n))
            return pd.DataFrame({
                'ts': [float(el[0]) for el in candles],
                'open': [float(el[1]) for el in candles],
                'high': [float(el[2]) for el in candles],
                'low': [float(el[3]) for el in candles],
                'close': [float(el[4]) for el in candles]
            })
        except Exception as err:
            self.logg.logger('GET_CANDLES_BG_ERROR', f'text: {err}')

    def df_candles_and_colour(self, symbol, colour=False, n=None):
        if n is None:
            response_df = self.df_candles(symbol, self.config.n_candles)
        else:
            response_df = self.df_candles(symbol, n)

        if colour:
            # True - red, False - green
            return response_df, list(response_df['close'])[-1] - list(response_df['open'])[-1] < 0
        else:
            return response_df

    def get_candles(self, n=None):
        # get candles data
        candles_basic, colour_last_candle = self.df_candles_and_colour(self.config.symbol_basic_usdt_bg, colour=True,
                                                                       n=n)
        return candles_basic, colour_last_candle

    # ----------------------------------------------------------------------------------------------------------------
    def get_quantity(self, price=None):
        try:
            available = float(
                self.iClient.mix_get_account(symbol=self.config.symbol_basic_usdt_bg,
                                             marginCoin='USDT')['data']['available'])
            if price is None:
                price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
                return str(int(available / price_now) - 1)
            else:
                return str(int(available / price) - 2)
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
                                                                 orderId=order_id)['data']['priceAvg']
                return price_order, quantity
            else:
                order_id = self.iClient.mix_place_order(symbol=symbol, marginCoin='USDT', size=quantity,
                                                        side=side, orderType='limit', price=str(price))['data'][
                    'orderId']
                # price_order = self.iClient.mix_get_order_details(symbol=self.config.symbol_basic_usdt_bg,
                #                                                  orderId=order_id)['data']['priceAvg']
                return order_id, quantity

        except Exception as err:
            self.logg.logger('ORDER_ERROR', f'text: {err}')

    def cancel_order(self, symbol, order_id):
        self.iClient.mix_cancel_order(symbol=symbol, marginCoin='USDT', orderId=order_id)

    def get_simple_profit(self, side, price_open, y):
        if side == 'long':
            return round(((y - price_open) / price_open) * 100, 3)
        elif side == 'short':
            return round(((price_open - y) / price_open) * 100, 3)

    def bg_get_profit(self, price_open, side):
        try:
            price_now = float(self.iClient.mix_get_depth(self.config.symbol_basic_usdt_bg)['data']['asks'][0][0])
            return self.get_simple_profit(side, price_open, price_now), price_now
        except Exception as err:
            self.logg.logger('GET_PROFIT_ERROR', f'text: {err}')

    def get_status(self, symbol, order_id):
        return self.iClient.mix_get_order_details(symbol=symbol, orderId=order_id)['data']['state'] == 'filled'
