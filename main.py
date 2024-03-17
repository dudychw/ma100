import datetime

from internal.trading import Trading
from pkg.logger import Logger
from test.history_test import HistoryTest
# try:
#     Trading().start()
# except Exception as err:
#     Logger().logger('ERROR', err)
start = datetime.datetime.now()
HistoryTest().history_test()
print(datetime.datetime.now() - start)