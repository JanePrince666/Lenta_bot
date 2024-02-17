import datetime


def time_of_function(function):
    def wrapped(*args):
        start = datetime.datetime.now()

        res = function(*args)

        end = datetime.datetime.now()
        print(f'{str(function)}: Время работы ' + str(end - start), file=open('report.txt', 'a'))
        # print(f"Время выполнения {str(function)}: {end}", )  ## вывод времени
        return res
    return wrapped
