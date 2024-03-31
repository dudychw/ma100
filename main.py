from internal.trading import Trading
from pkg.logger import Logger

try:
    Trading().start('break_ma100')
except Exception as err:
    Logger().logger('ERROR', err)

