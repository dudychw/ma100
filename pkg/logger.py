import datetime


class Logger:

    def logger(self, status, message):
        with open(f'../ma100/doc/logger.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: {message} \n')
            file.close()

