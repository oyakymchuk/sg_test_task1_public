from create_and_fill_db import create_and_fill_db
from monitoring import run_monitoring
from loggerinitializer import *

if __name__ == '__main__':
    initialize_logger()

    flag = True
    while flag:
        a = str(input("What do you want to do? [1-create/reset database; 2-run monitoring; 3-exit]: "))
        print('\n')
        if a == '1':
            create_and_fill_db()
            print('\n')
        elif a == '2':
            run_monitoring()
            print('\n')
        elif a == '3':
            flag = False
        else:
            logging.info('Wrong input. Try again after restart.')