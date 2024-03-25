import datetime
import random

from config.config import Config
from pkg.binance_api import Binance_API
from pkg.bitget_api import BitGetApi
from pkg.indicators import Indicator
from pkg.logger import Logger

import pandas as pd
import numpy as np


class HistoryTest:
    def __init__(self):
        self.bc_client = Binance_API()
        self.logg = Logger()
        self.config = Config()
        self.indicator = Indicator()

        self.period = self.config.period_int
        self.hour_skip = 0
        self.stop_hour_skip = 10

    def history_test(self):
        n = 360 * 3

        time_end = datetime.datetime.now()
        time_start = time_end - datetime.timedelta(days=5)
        candles = self.bc_client.df_candles_time(symbol=self.config.symbol_basic_usdt_bc,
                                                 time_start=int(time_start.timestamp()) * 1000,
                                                 time_end=int(time_end.timestamp()) * 1000,
                                                 )

        for i in range(n // 5 - 1):
            time_end = time_start
            time_start = time_end - datetime.timedelta(days=5)
            add_candles = self.bc_client.df_candles_time(symbol=self.config.symbol_basic_usdt_bc,
                                                         time_start=int(time_start.timestamp()) * 1000,
                                                         time_end=int(time_end.timestamp()) * 1000,
                                                         )
            candles = pd.concat([add_candles, candles], ignore_index=True, sort=False)

        close = list(candles['close'])[99:]
        ma100 = self.indicator.ma100(candles)[99:]

        data = []
        for i in range(1, len(close)):
            if ((close[i - 1] < ma100[i - 1] and close[i] > ma100[i]) or
                    (close[i - 1] > ma100[i - 1] and close[i] < ma100[i])):
                trend_direction = 'short' if close[i] < ma100[i] else 'long'
                time_break = [datetime.datetime.fromtimestamp(el / 1000) for el in candles['ts']][i] + \
                             datetime.timedelta(days=1, minutes=45)
                data.append([i + 99, trend_direction, ma100[i], time_break])
        print('data received')

        while self.hour_skip <= self.stop_hour_skip:
            # добавить цену входа
            ans = {'time': [], 'trend': [], 'first_cndl%': [], 'proof_cndl%': [], 'price_brak_ma100': [], 'price_back_break': [],
                   # 'open_proof_cndl': [],
                   'profit_down%': [],
                   'max_cndl%': [], 'profit%': [],
                   'not_back_break': [], 'is_4%distance': [None]}
            for i in range(len(data) - 1):
                break_ma100 = data[i][2]
                opn = list(candles['open'])[data[i][0] + 1:data[i + 1][0]]
                close = list(candles['close'])[data[i][0] + 1:data[i + 1][0]]

                # true - green, false - red
                proof_cndl_perc = [close[i] - opn[i] > 0 for i in range(len(opn))]

                if data[i][1] == 'long':
                    a = list(candles['high'])[data[i][0]:data[i + 1][0]]

                    ind = proof_cndl_perc.index(True) + 1 if len(a) != 1 and True in proof_cndl_perc else None
                    perc_dist = [round((el - break_ma100) / break_ma100 * 100, 2) for el in a]
                else:
                    a = list(candles['low'])[data[i][0]:data[i + 1][0]]
                    ind = proof_cndl_perc.index(False) + 1 if len(a) != 1 and False in proof_cndl_perc else None
                    perc_dist = [round((break_ma100 - el) / break_ma100 * 100, 2) for el in a]

                ans['time'].append(f'{data[i][3]} - {data[i + 1][3]}')
                ans['trend'].append(data[i][1])
                ans['first_cndl%'].append(perc_dist[0])
                ans['max_cndl%'].append(
                    max(perc_dist[self.hour_skip * 4:]) if len(perc_dist) >= self.hour_skip * 4 + 1 else None)
                ans['not_back_break'].append(len(perc_dist) != 1)
                ans['is_4%distance'].append(
                    len(perc_dist) >= self.hour_skip * 4 + 1 and max(perc_dist[self.hour_skip * 4:]) >= 4)
                ans['proof_cndl%'].append(perc_dist[ind] if not (ind is None) else None)

                ans['price_brak_ma100'].append(close[ind - 1] if not(ind is None) else None)
                ans['price_back_break'].append(list(candles['close'])[data[i + 1][0]])
                ans['profit_down%'].append(
                    (-1 if (data[i][1] == 'long' and close[ind - 1] > list(candles['close'])[data[i + 1][0]]) or
                           (data[i][1] == 'short' and close[ind - 1] < list(candles['close'])[data[i + 1][0]]) else 1) *
                    round(abs(close[ind - 1] - list(candles['close'])[data[i + 1][0]]) / close[ind - 1] * 100, 2) if not(ind is None) else None)

                d = round(abs(close[ind - 1] - break_ma100) / break_ma100 * 100, 2) if not (ind is None) else None
                # ans['open_proof_cndl'].append(d)
                ans['profit%'].append(
                    max(perc_dist[self.hour_skip * 4:]) - d if not (ind is None) and len(perc_dist) >= self.hour_skip * 4 + 1 else False)

            ans['is_4%distance'] = ans['is_4%distance'][:-1]
            out = pd.DataFrame.from_dict(ans)

            path = './test/result/history_test_all.txt'

            # with open(path, "w") as f:
            #     f.write("")
            #
            # with open(path, 'a') as f:
            #     text = out.to_string(header=True, index=True)
            #     f.write(text)
            # -------------------------------------------------

            out_order = out.loc[
                (out['not_back_break']) & (out['is_4%distance']) & (out['proof_cndl%'] > 0) & (out['profit%'])]

            profit = 1
            c = 0
            for el in range(len(list(out_order['profit%']))):
                if list(out_order['profit%'])[el] < 1.5:
                    profit *= 1 - abs(list(out_order['profit_down%'])[el]) / 100
                    c += 1
                else:
                    # profit *= (el / (3 * 100) + 1)
                    profit *= 1.02
            profit = round((profit - 1) * 100, 2)

            out_order = out_order.sort_values('profit%', ascending=False)

            # path = './test/result/history_test.txt'

            # with open(path, "w") as f:
            #     f.write("")
            #
            # with open(path, 'a') as f:
            #     text = out_order.to_string(header=True, index=True)
            #     f.write(text)

            with open('./test/result/result.txt', 'a') as f:
                a = round((c / len(list(out_order['profit%']))) * 100, 2)
                f.write(
                    f"{datetime.datetime.now()} | fail - {c} ({a}%); good - {len(list(out_order['profit%'])) - c} ({100 - a}%) | profit: {profit} | time_test: {n + 5} | time_skip: {self.hour_skip}\n")
            print(self.hour_skip)
            self.hour_skip += 1
