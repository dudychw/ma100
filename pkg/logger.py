import datetime


class Logger:

    def logger(self, status, message):
        with open(f'../ma100/logs/logger.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: text: {message} \n')
            file.close()

    def speed_test_logger(self, status, time_test):
        with open(f'../ma100/logs/speed_test/speed_test.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: time = {datetime.datetime.now() - time_test} \n')
            file.close()
