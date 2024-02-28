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
        self.check = self.config.check

        # trading status
        self.trade = False
        self.price_open = None
        self.expected_price_open = None
        self.order_quantity = None

        self.side = ''
        self.time_trade = ''
        self.flag_33 = True
        self.time_activate_flag_33 = ''

    # --------------------------------------------------------------------------------------------------------------------

    def start(self):
        self.logg.logger('START_BOT', 'start')
        print('I alive')
        # start infinity cycle
        while True:
            pass
