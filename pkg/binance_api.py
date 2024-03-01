import pandas as pd
from config.config import Config
from pkg.logger import Logger
# from binance.um_futures import UMFutures
from binance.spot import Spot


class Binance_API:
    def __init__(self):
        self.config = Config()
        self.logg = Logger()
        # self.um_futures_client = UMFutures()
        self.binance_spot_client = Spot()

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

    def df_candles_and_colour(self, symbol, colour=False):
        response_df = self.df_candles(symbol, self.config.n_candles)

        if colour:
            return response_df, list(response_df['close'])[-1] - list(response_df['open'])[-1] < 0
        else:
            return response_df

    def get_ratio_body_and_shadow(self, symbol):
        response_df = self.df_candles(symbol, self.config.n_candles)
        l_open, l_high, l_low, l_close = [list(response_df[el])[-1] for el in ['open', 'high', 'low', 'close']]
        if (l_close - l_open) != 0:
            return response_df, abs((l_open - l_low + l_high - l_close) / (l_close - l_open)) < 2
        return response_df, None

    def get_candles(self):
        # get candles data
        candles_basic, colour_last_candle = self.df_candles_and_colour(self.config.symbol_basic_usdt_bc, colour=True)
        # candles_btc = self.df_candles_and_colour(self.config.symbol_btc_usdt_bc)
        return candles_basic, colour_last_candle

    def get_volume(self):
        try:
            # data = self.um_futures_client.klines(symbol=self.config.symbol_btc_usdt_bc,
            #                                      interval=self.config.period_bc, limit=2)
            data = self.binance_spot_client.klines(symbol=self.config.symbol_btc_usdt_bc,
                                                   interval=self.config.period_bc, limit=2)
            df_data = []
            for i in range(2):
                df_data.append({'open': float(data[i][1]), 'high': float(data[i][2]), 'low': float(data[i][3]),
                                'close': float(data[i][4]), 'volume': float(data[i][5])})
            last_bc_candle, now_bc_candle = df_data[0], df_data[1]
            colour = int((now_bc_candle['close'] - now_bc_candle['open']) < 0)
            ratio_volume = now_bc_candle['volume'] / last_bc_candle['volume']

            return colour, ratio_volume
        except Exception as err:
            Logger().logger('BINANCE_ERROR', f'text: {err}')