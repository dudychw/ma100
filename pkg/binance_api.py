import pandas as pd
from config.config import Config
from pkg.logger import Logger
from binance.spot import Spot


class Binance_API:
    def __init__(self):
        self.config = Config()
        self.logg = Logger()
        self.binance_spot_client = Spot()

    def df_candles_time(self, symbol, time_start, time_end):
        try:
            # get candles data
            candles = [(el[0], float(el[1]), float(el[2]), float(el[3]), float(el[4]))
                       for el in self.binance_spot_client.klines(symbol=symbol, interval=Config.period_bc,
                                                                 startTime=time_start, endTime=time_end)]

            return pd.DataFrame({
                'ts': [float(el[0]) for el in candles],
                'open': [float(el[1]) for el in candles],
                'high': [float(el[2]) for el in candles],
                'low': [float(el[3]) for el in candles],
                'close': [float(el[4]) for el in candles]
            })
        except Exception as err:
            self.logg.logger('GET_CANDLES_ERROR', f'text: {err}')

    def df_candles(self, symbol, n):
        try:
            # get candles data
            candles = [(el[0], float(el[1]), float(el[2]), float(el[3]), float(el[4]))
                       for el in self.binance_spot_client.klines(symbol=symbol, interval=Config.period_bc, limit=n)]
            return pd.DataFrame({
                'ts': [float(el[0]) for el in candles],
                'open': [float(el[1]) for el in candles],
                'high': [float(el[2]) for el in candles],
                'low': [float(el[3]) for el in candles],
                'close': [float(el[4]) for el in candles]
            })
        except Exception as err:
            self.logg.logger('GET_CANDLES_ERROR', f'text: {err}')

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
        candles_basic, colour_last_candle = self.df_candles_and_colour(self.config.symbol_basic_usdt_bc, colour=True,
                                                                       n=n)
        return candles_basic, colour_last_candle
