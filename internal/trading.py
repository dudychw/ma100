from internal.internal.break_ma100 import BreakMa100
from pkg.logger import Logger


# Название модуля, содержащего класс


class Trading:
    def __init__(self):
        self.logg = Logger()

    def start(self, strategy):
        self.logg.logger('START_BOT', f'strategy: {strategy}')

        if strategy == 'break_ma100':
            BreakMa100().start()
        if strategy == 'rebound':
            pass