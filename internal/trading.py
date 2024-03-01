import datetime
import time
from pkg.bitget_api import BitGetApi
from pkg.binance_api import Binance_API
from pkg.indicators import Indicator
from pkg.logger import Logger
from config.config import Config


class Trading:
    def __init__(self):
        # client class
        self.bg_client = BitGetApi()
        self.bc_client = Binance_API()
        self.logg = Logger()
        self.config = Config()
        self.indicator = Indicator()

        # other data
        self.period = self.config.period_int

        # trading status
        self.trade = True
        self.price_open = None
        self.expected_price_open = None
        self.order_quantity = None

        self.side = ''
        self.time_trade = ''

        self.stop_loss = 0
        self.take_profit = 0

        # None - пункт не активизирован
        # True - идём пробивать и держим позицию
        # False - вышли из позиции, но не откатились на 4% от ma100
        self.rule_break_ma100 = None

        self.rule_rebound_ma100 = None

    # --------------------------------------------------------------------------------------------------------------------

    def start(self):
        self.logg.logger('START_BOT', 'start')
        print('alive')

        while True:
            if self.trade:
                if (datetime.datetime.now().minute + 1) % self.period == 0 and \
                        datetime.datetime.now().second == 59 and datetime.datetime.now().microsecond > 99990:

                    # data
                    candles, color = self.bc_client.get_candles()
                    close = list(candles['close'])
                    ma100 = self.indicator.ma100(candles)

                    if self.rule_break_ma100 is None and abs(ma100[-1] - close[-1]) / ma100[-1] >= 0.04:
                        self.rule_break_ma100 = True

                    if self.rule_break_ma100:
                        if not color and close[-2] < ma100[-2] and close[-1] > ma100[-1]:  # long

                            # update data
                            time.sleep(self.config.period_int * 60 - 0.01)
                            candles, color = self.bc_client.get_candles()
                            close = list(candles['close'])
                            ma100 = self.indicator.ma100(candles)

                            proof_candle = True

                            while True:
                                if close[-2] < ma100[-2] and close[-1] > ma100[-1]:

                                    if proof_candle and abs(ma100[-1] - close[-1]) / ma100[-1] >= 0.01:
                                        break
                                    else:
                                        proof_candle = False

                                    if not color:
                                        self.price_open, self.order_quantity = self.bg_client.get_order(
                                            self.config.symbol_basic_usdt_bg, 'open_long')
                                        self.time_trade = datetime.datetime.now()
                                        self.trade = False
                                        self.take_profit = 2
                                        break
                                    else:
                                        time.sleep(self.config.period_int * 60 - 0.01)
                                        candles, color = self.bc_client.get_candles()
                                        close = list(candles['close'])
                                        ma100 = self.indicator.ma100(candles)
                                else:
                                    break

                        elif color and close[-2] > ma100[-2] and close[-1] < ma100[-1]:  # short

                            # update data
                            time.sleep(self.config.period_int * 60 - 0.01)
                            candles, color = self.bc_client.get_candles()
                            close = list(candles['close'])
                            ma100 = self.indicator.ma100(candles)

                            proof_candle = True

                            while True:
                                if close[-2] > ma100[-2] and close[-1] < ma100[-1]:

                                    if proof_candle and abs(ma100[-1] - close[-1]) / ma100[-1] >= 0.01:
                                        break
                                    else:
                                        proof_candle = False

                                    if color:
                                        self.price_open, self.order_quantity = self.bg_client.get_order(
                                            self.config.symbol_basic_usdt_bg, 'open_short')
                                        self.time_trade = datetime.datetime.now()
                                        self.trade = False
                                        self.take_profit = 2
                                        break
                                    else:
                                        time.sleep(self.config.period_int * 60 - 0.01)
                                        candles, color = self.bc_client.get_candles()
                                        close = list(candles['close'])
                                        ma100 = self.indicator.ma100(candles)
                                else:
                                    break
            else:
                pass