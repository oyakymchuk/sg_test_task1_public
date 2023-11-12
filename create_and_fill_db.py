import sqlite3
import numpy as np

from datetime import datetime

from config import CONFIG, DATETIME_FORMAT
from sql_string import SQL_String
from loggerinitializer import *

GENERATION_DAYS_PERIOD = 30

def create_db(cursor):
    '''
        Creates database with two tables Orders and Transactions.
    '''
    cursor.execute('DROP TABLE IF EXISTS Orders;')
    cursor.execute(SQL_String.create_table_orders())
    cursor.execute('DROP TABLE IF EXISTS Transactions;')
    cursor.execute(SQL_String.create_table_transactions())

def dt64_2_str(dt64):
    dt = dt64.astype(datetime)
    return datetime.strftime(dt, DATETIME_FORMAT)

def generate_order(order_id):
    '''
        Returns 2 lists of input data:
            - into Orders table,
            - into Transactions table
    '''
    # Generate input into Orders table.
    o_created_date = np.datetime64('now') - np.timedelta64(np.random.randint(GENERATION_DAYS_PERIOD), 'D')
    # Let's imagine we have 10 merchants.
    o_merchant_id = np.random.randint(10)
    order_input = (order_id, dt64_2_str(o_created_date), o_merchant_id+1)

    # Generate inputs into Transactions table.
    transaction_inputs = list()
    # Let's assume it is common case that authentication transactions appear within 1 hour since record in Orders appered.
    t_first_created_date = o_created_date + np.random.randint(3600)
    # Let's assume that we have 5% of failed authentication transactions.
    t_first_status = 'success' if np.random.binomial(1, 0.95) else 'fail'

    t_auth_input = (dt64_2_str(t_first_created_date), 'auth', order_id, t_first_status)
    transaction_inputs.append(t_auth_input)
    
    # Let's assume we have 10% of incomplete orders.
    # Also, orders with failed authentication transactions should not be completed.
    anomaly_flag = np.random.binomial(1, 0.10)
    if (not anomaly_flag) and (t_first_status == 'success'):
        # Let's assume that transactions could be canceled in 5% of cases.
        t_second_type = 'settle' if np.random.binomial(1, 0.95) else 'void'
        t_second_created_date = t_first_created_date + np.random.randint(7*3_600)
        t_second_status = 'success' if np.random.binomial(1, 0.9) else 'fail'
        t_second_input = (dt64_2_str(t_second_created_date), t_second_type, order_id, t_second_status)
        transaction_inputs.append(t_second_input)
    return order_input, transaction_inputs

def fill_database(n, cursor):
    for i in range(n):
        order_input, transactions_inputs = generate_order(i+1)
        cursor.execute(SQL_String.insert_into_orders(order_input))
        for transaction in transactions_inputs:
            cursor.execute(SQL_String.insert_into_transactions(transaction))

def create_and_fill_db():
    logging.info(f"Tool for creation and filling database started.")

    with sqlite3.connect(CONFIG['database_name']) as connection:
        cursor = connection.cursor()
        create_db(cursor=cursor)
        fill_database(n=CONFIG['orders_to_insert'], cursor=cursor)
    logging.info(f"It was inserted 100 orders into {CONFIG['database_name']}")
    
    logging.info("Tool finished.")