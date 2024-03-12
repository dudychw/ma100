from finta import TA
from pkg.logger import Logger


class Indicator:
    def ma100(self, candles):
        try:
            return list(TA.SMA(candles, 100))
            # return list(TA.SMA(candles, 100))[-2:]
        except Exception as err:
            Logger().logger('MA100_ERROR', f'text: {err}')
