import datetime


class Logger:

    def logger(self, status, message):
        with open(f'../ma100/logs/logger.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: text: {message} \n')
            file.close()
        with open(f'../ma100/logs/history_logs.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: text: {message} \n')
            file.close()
