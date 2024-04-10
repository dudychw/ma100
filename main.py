from internal.trading import Trading
# from internal.general import Trading
from pkg.logger import Logger

try:
    Trading().start('break_ma100')
    # Trading().start()
except Exception as err:
    Logger().logger('ERROR', err)
