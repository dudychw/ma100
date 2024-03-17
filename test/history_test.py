import datetime

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

    def history_test(self):
        n = 295

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
        # print(candles.to_string())

        close = list(candles['close'])[99:]
        ma100 = self.indicator.ma100(candles)[99:]

        # print(len(close), close)
        # print(len(ma100), ma100)
        data = []
        for i in range(1, len(close)):
            if ((close[i - 1] < ma100[i - 1] and close[i] > ma100[i]) or
                    (close[i - 1] > ma100[i - 1] and close[i] < ma100[i])):
                trend_direction = 'short' if close[i] < ma100[i] else 'long'
                time_break = [datetime.datetime.fromtimestamp(el / 1000) for el in candles['ts']][i] + \
                             datetime.timedelta(days=1, minutes=45)
                data.append([i + 99, trend_direction, ma100[i], time_break])

        # добавить цену входа
        #
        ans = {'time': [], 'trend': [], 'first_cndl%': [], 'proof_cndl%': [], 'open_proof_cndl': [],
               'max_cndl%': [], 'profit%': [],
               'not_back_break': [], 'is_1%_first_cndl': [], 'is_1%_proof_cndl': [], 'is_4%distance': [None]}
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
            # print(perc_dist)

            ans['time'].append(f'{data[i][3]} - {data[i + 1][3].time()}')
            ans['trend'].append(data[i][1])
            ans['first_cndl%'].append(perc_dist[0])
            ans['max_cndl%'].append(max(perc_dist))
            ans['not_back_break'].append(len(perc_dist) != 1)
            ans['is_4%distance'].append(max(perc_dist) >= 4)
            ans['is_1%_first_cndl'].append(perc_dist[0] < 1)
            ans['is_1%_proof_cndl'].append(not (ind is None) and perc_dist[ind] < 1)
            ans['proof_cndl%'].append(perc_dist[ind] if not (ind is None) else None)

            d = round(abs(close[ind - 1] - break_ma100) / break_ma100 * 100, 2) if not (ind is None) else None
            ans['open_proof_cndl'].append(d)
            ans['profit%'].append(max(perc_dist) - d if not (ind is None) else None)

        ans['is_4%distance'] = ans['is_4%distance'][:-1]
        out = pd.DataFrame.from_dict(ans)
        # print(out.to_string())

        # out = out.loc[
        #     (out['not_back_break']) & (out['is_4%distance']) & (out['is_1%_first_cndl']) & (out['is_1%_proof_cndl'])]
        out = out.loc[
            (out['not_back_break']) & (out['is_4%distance']) & (out['proof_cndl%'] > 0)]
        # print(out.to_string())
        profit = 1
        dp = []
        for el in list(out['profit%']):
            if el < 1:
                profit *= 0.98
                dp.append(el)
            else:
                profit *= (el / 100 + 1)
        profit = round((profit - 1) * 100, 2)
        print(len(dp), sorted(dp))
        print(sum(dp) / len(dp))

        path = './test/history_test.txt'

        with open(path, "w") as f:
            f.write("")

        with open(path, 'a') as f:
            text = out.to_string(header=True, index=True)
            f.write(text)
            f.write('\nprofit - ' + str(profit) + '%')

# profit - 155.76% по всем правилам
# profit - 1852.87% если отрубить правило 1% и смотреть по максимуму
# profit - 531.08% если не добирает до 1% прибыли при отключении правила 1% и дохода до минимального стоп-лосса (-2%)
# profit - 165.15% если не добирает до 2% прибыли при отключении правила 1% и дохода до минимального стоп-лосса (-2%)

# profit - 936.49%
#