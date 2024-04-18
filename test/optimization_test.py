import datetime
import random
import time
import pandas as pd

from pkg.bitget_api import BitGetApi


class Optimization:
    def __init__(self):
        # client class
        self.bg_client = BitGetApi()
        self.period = 1
        self.last_candle = 0
        self.pre_last_candle = 0

    def v1(self):
        # ~ 0.418 sec
        data = []
        for i in range(200):
            start = datetime.datetime.now()
            candles, color = self.bg_client.get_candles()
            data.append((datetime.datetime.now() - start).microseconds)
            # time.sleep(random.randint(1, 3))
            # print(i)
        print(min(data), max(data))
        print(sum(data) / len(data) / 10 ** 6)

    def v2(self):
        # ~0.415 sec
        a = []
        # candles, color = self.bg_client.get_candles()
        for i in range(200):
            st = datetime.datetime.now()
            # self.pre_last_candle = self.last_candle
            self.last_candle = self.bg_client.get_last_candle()
            # candles.drop(index=candles.index[0], axis=0, inplace=True)
            # candles.loc[candles.index[-1] + 1] = self.last_candle
            a.append((datetime.datetime.now() - st).microseconds)
        print(min(a), max(a))
        print(sum(a) / len(a) / 10 ** 6)

Optimization().v1()
Optimization().v2()