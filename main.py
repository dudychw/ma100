from internal.trading import Trading
# from internal.general import Trading
from test.history_test import HistoryTest
from pkg.logger import Logger

# try:
#     Trading().start('break_ma100')
# except Exception as err:
#     Logger().logger('ERROR', err)
HistoryTest().history_test()