import datetime

from internal.trading import Trading
from pkg.logger import Logger

try:
    Trading().start('rebound')
except Exception as err:
    Logger().logger('ERROR', err)

