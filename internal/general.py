import datetime
import sys
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
        self.order_id = None

        self.side = ''
        self.trend_direction = None
        self.internal_trend_direction = None
        self.time_trade = ''

        self.stop_loss = -1000
        self.take_profit = 0

        # None - пункт не активизирован
        # True - идём пробивать и держим позицию
        # False - вышли из позиции, но не откатились на 4% от ma100
        self.rule_break_ma100 = None
        self.time_rule_break_ma100 = None
        self.price_break_ma100 = None

        self.rule_rebound_ma100 = None
        self.hour_skip_rule = True
        self.time_hour_skip_rule = datetime.datetime.now() - datetime.timedelta(hours=1)

    # --------------------------------------------------------------------------------------------------------------------
    def open_position_break_ma100(self, side):
        try:
            self.price_open, self.order_quantity = self.bg_client.get_order(
                self.config.symbol_basic_usdt_bg, f'open_{side}')
            self.logg.logger('OPEN_POSITION', f'price_open = {self.price_open} ({side})')
            self.time_trade = datetime.datetime.now()
            self.side = side
            self.trade = False

        except Exception as err:
            self.logg.logger(f'ERROR_OPEN_POSITION', f'text: {err}')

    def close_position(self, side, logg_text, type_close=None):
        try:
            price_close, self.order_quantity = self.bg_client.get_order(
                self.config.symbol_basic_usdt_bg, f'close_{side}', self.order_quantity)

            self.logg.logger('EXIT_FROM_POSITION', f'{logg_text}; price_close = {price_close}; ({side})')

            self.side = ''
            self.stop_loss = -1000

            self.price_open = None
            self.order_quantity = None
            self.trade = True
            self.internal_trend_direction = None

            if type_close == 'break':
                self.rule_break_ma100 = None
            elif type_close == 'rebound':
                self.rule_rebound_ma100 = None

        except Exception as err:
            self.logg.logger(f'ERROR_EXIT_FROM_POSITION', f'status: {logg_text} text: {err}')

    def get_percentage_distance(self, price_now):
        return abs(self.price_break_ma100 - price_now) / self.price_break_ma100

    def get_close_candle_time(self):
        return (datetime.datetime.now().minute + 1) % self.period == 0 and \
            datetime.datetime.now().second == 59 and datetime.datetime.now().microsecond > 900000

    # --------------------------------------------------------------------------------------------------------------------

    def start(self):
        print('\nalive')

        # getting data  first break
        n = 500
        candles, color = self.bg_client.get_candles(n=n)
        close = list(candles['close'])
        ma100 = self.indicator.ma100(candles)
        for i in range(n - 1, 1, -1):
            if ((close[i - 1] < ma100[i - 1] and close[i] > ma100[i]) or
                    (close[i - 1] > ma100[i - 1] and close[i] < ma100[i])):
                self.price_break_ma100 = ma100[i]
                self.time_rule_break_ma100 = [datetime.datetime.fromtimestamp(el / 1000) for el in candles['ts']][
                                                 i] + datetime.timedelta(minutes=self.period)
                self.trend_direction = 'short' if close[-1] < self.price_break_ma100 else 'long'
                self.logg.logger('FIRST_BREAK_MA100',
                                 f'price_break_ma100 = {self.price_break_ma100}; side = {self.trend_direction};'
                                 f' time_break = {self.time_rule_break_ma100}')
                break

        while True:
            if self.trade:
                if self.get_close_candle_time():
                    # data
                    candles, color = self.bg_client.get_candles()
                    close = list(candles['close'])
                    ma100 = self.indicator.ma100(candles)

                    # control break ma100
                    if ((not color and close[-2] < ma100[-2] and close[-1] > ma100[-1]) or
                            (color and close[-2] > ma100[-2] and close[-1] < ma100[-1])):
                        self.price_break_ma100 = ma100[-1]
                        self.time_rule_break_ma100 = datetime.datetime.now()
                        self.trend_direction = 'long' if not color else 'short'
                        self.logg.logger('BREAK_MA100',
                                         f'price_break_ma100 = {self.price_break_ma100}; side = {self.trend_direction};'
                                         f' time_break = {self.time_rule_break_ma100}')

                    # ---------------------------------------------------------------------------------------------
                    # rule_break_ma100
                    try:
                        if self.rule_break_ma100 is None and (
                                datetime.datetime.now() - self.time_rule_break_ma100).seconds / 3600 >= 4:
                            if self.trend_direction == 'short' and close[-1] < ma100[-1] and \
                                    self.get_percentage_distance(list(candles['low'])[-1]) >= 0.04:
                                self.rule_break_ma100 = True
                                self.logg.logger('APPROVE_RULE_BREAK_MA100',
                                                 f'price_for_distance = {list(candles["low"])[-1]}; '
                                                 f'side_accuses = long')
                            elif self.trend_direction == 'long' and close[-1] > ma100[-1] and \
                                    self.get_percentage_distance(list(candles['high'])[-1]) >= 0.04:
                                self.rule_break_ma100 = True
                                self.logg.logger('APPROVE_RULE_BREAK_MA100',
                                                 f'price_for_distance = {list(candles["high"])[-1]}; '
                                                 f'side_accuses = short')

                        if self.rule_break_ma100:

                            if ((not color and close[-2] < ma100[-2] and close[-1] > ma100[-1]) or
                                    (color and close[-2] > ma100[-2] and close[-1] < ma100[-1])):

                                self.trend_direction = 'long' if not color else 'short'
                                self.price_break_ma100 = ma100[-1]
                                self.logg.logger('POTENTIAL_BREAK_MA100',
                                                 f'price_break_ma100 = {self.price_break_ma100}; '
                                                 f'side = {self.trend_direction}')
                                self.time_rule_break_ma100 = datetime.datetime.now()

                                # found proof candle
                                count_attempt = 0
                                while True:
                                    if (close[-1] >= ma100[-1] and self.trend_direction == 'long') or (
                                            close[-1] <= ma100[-1] and self.trend_direction == 'short'):

                                        if count_attempt != 0 and self.internal_trend_direction == self.trend_direction:
                                            self.open_position_break_ma100(self.trend_direction)
                                            break
                                        else:
                                            self.logg.logger(
                                                'ATTEMPT_OPEN_POSITION', f'num - {count_attempt}; '
                                                                         f'side={self.internal_trend_direction}')
                                            count_attempt += 1
                                            time.sleep(self.config.period_int * 60 - 0.05)
                                            candles, color = self.bg_client.get_candles()
                                            self.internal_trend_direction = 'long' if not color else 'short'
                                            close = list(candles['close'])
                                            ma100 = self.indicator.ma100(candles)
                                    else:
                                        self.price_break_ma100 = ma100[-1]
                                        self.trend_direction = 'long' if not color else 'short'
                                        self.logg.logger('BACK_BREAK_MA100',
                                                         f'price_break_ma100 = {self.price_break_ma100}')
                                        self.time_rule_break_ma100 = datetime.datetime.now()
                                        self.rule_break_ma100 = None
                                        break

                    except Exception as err:
                        self.logg.logger('ERROR_RULE_BREAK_MA100', err)
                        sys.exit()

                    # ----------------------------------------------------------------------------------------------
                    #  rule_rebound_ma100
                    try:
                        if self.rule_rebound_ma100 is None and (
                                datetime.datetime.now() - self.time_rule_break_ma100).seconds / 3600 >= 2 and \
                                (datetime.datetime.now() - self.time_hour_skip_rule).seconds / 3600 >= 2:

                            if self.trend_direction == 'short' and close[-1] < ma100[-1] and \
                                    self.get_percentage_distance(list(candles['low'])[-1]) >= 2:
                                self.rule_rebound_ma100 = True
                                self.logg.logger('APPROVE_RULE_REBOUND_MA100',
                                                 f'price_for_distance = {list(candles["low"])[-1]}; '
                                                 f'side_accuses = long')
                            elif self.trend_direction == 'long' and close[-1] > ma100[-1] and \
                                    self.get_percentage_distance(list(candles['high'])[-1]) >= 2:
                                self.rule_rebound_ma100 = True
                                self.logg.logger('APPROVE_RULE_REBOUND_MA100',
                                                 f'price_for_distance = {list(candles["high"])[-1]}; '
                                                 f'side_accuses = short')

                        if self.rule_rebound_ma100:
                            # cancel old limit order
                            if not (self.order_id is None):
                                self.bg_client.cancel_order(symbol=self.config.symbol_basic_usdt_bg,
                                                            order_id=self.order_id)
                                self.logg.logger('CANCEL_LIMIT_ORDER', 'cancel limit order')

                            # side new limit order
                            if close[-1] < ma100[-1]:
                                local_side = 'open_short'
                            else:
                                local_side = 'open_long'

                            price_limit_order = round(sum(close[-100:]) / 100, 4)
                            self.order_id, self.order_quantity = self.bg_client.get_order(
                                symbol=self.config.symbol_basic_usdt_bg, side=local_side, price=price_limit_order)

                            self.price_open = price_limit_order
                            self.logg.logger('OPEN_LIMIT_ORDER', f'price = {price_limit_order}')

                            while True:
                                if self.bg_client.get_status(symbol=self.config.symbol_basic_usdt_bg,
                                                             order_id=self.order_id):
                                    self.logg.logger('LIMIT_ORDER_FILLED', 'filled')
                                    self.trade = False
                                    self.time_trade = datetime.datetime.now()
                                    self.take_profit = 1
                                    self.side = local_side[5:]
                                    break

                                if (datetime.datetime.now().minute + 1) % self.period == 0 and \
                                        datetime.datetime.now().second >= 59:
                                    break

                    except Exception as err:
                        self.logg.logger('ERROR_RULE_REBOUND_MA100', err)
                        sys.exit()
                    # ---------------------------------------------------------------------------------------------

            else:
                profit, price_now = self.bg_client.bg_get_profit(self.price_open, self.side)

                # if profit <= self.stop_loss:
                # self.close_position(self.side, f"exit due stop-loss ({profit}%)")

                # data
                candles, color = self.bg_client.get_candles()
                close = list(candles['close'])
                ma100 = self.indicator.ma100(candles)

                if self.rule_break_ma100:
                    if profit <= self.stop_loss:
                        self.close_position(self.side, f'exit due stop-loss ({profit}%)', 'break')

                    # rebound down
                    if (datetime.datetime.now().minute + 1) % self.period == 0 and \
                            datetime.datetime.now().second == 59:
                        if ((close[-2] < ma100[-2] and close[-1] > ma100[-1]) or
                                (close[-2] > ma100[-2] and close[-1] < ma100[-1])):
                            self.close_position(self.side, f'exit due bounce down', 'break')

                    # trailing stop-loss
                    if profit >= 1.5:
                        self.stop_loss = max(profit - 0.5, self.stop_loss)

                    if profit < 1.5 and (datetime.datetime.now() - self.time_trade).seconds / 3600 >= 5:
                        self.close_position(self.side, f'exit due 5 hour stagnation ({profit}%)', 'break')

                elif self.rule_rebound_ma100:
                    if profit <= self.stop_loss:
                        self.close_position(self.side, f'exit due stop-loss ({profit}%)', 'rebound')

                    if profit >= self.take_profit:
                        self.close_position(self.side, f'exit due take-profit ({profit}%)', 'rebound')

                    # выход при закрытии свечки в диапазоне -0,05% до +-бесконечности, закрываем рыночным ордером
                    if self.get_close_candle_time() and ((self.side == 'short' and close[-1] >= ma100[-1] * 0.995) or (
                            self.side == 'long' and close[-1] <= ma100[-1] * 1.005)):
                        self.close_position(self.side, f'exit due failed rebound', 'rebound')
                        local_side = self.side
                        # check rebound for 1-hour blocked rule_rebound_ma100
                        time.sleep(self.config.period_int * 60 - 0.01)
                        candles, color = self.bg_client.get_candles()
                        close = list(candles['close'])
                        ma100 = self.indicator.ma100(candles)

                        if (local_side == 'long' and close[-1] >= ma100[-1]) or \
                                (local_side == 'short' and close[-1] <= ma100[-1]):
                            self.time_hour_skip_rule = datetime.datetime.now()
                            self.logg.logger('ACTIVATE_1_HOUR_SKIP', '1 hour skip')

                    if profit >= 0.5 and self.stop_loss == -1000:
                        self.stop_loss = 0.2
                        self.logg.logger('STOP-LOSS_CHANGED', 'first step')
                    if profit >= 0.9 and self.stop_loss > 0:
                        self.stop_loss = 0.5
                        self.logg.logger('STOP-LOSS_CHANGED', 'second step')
