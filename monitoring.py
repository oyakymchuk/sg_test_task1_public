import sqlite3
import requests
import os
import gspread
import warnings

from pandas import DataFrame
from datetime import datetime
from getpass import getuser

from config import CONFIG
from sql_string import SQL_String
from loggerinitializer import *

def get_not_incomplete_orders():
    try: 
        with sqlite3.connect(CONFIG['database_name']) as connection:
            logging.info("Database connection successfuly established.")
            cursor = connection.cursor()
            problem_orders = cursor.execute(SQL_String.get_not_finished_transactions_query()).fetchall()
            logging.info(f"It was founded {len(problem_orders)} incomplete orders.")
            df_problem_orders = DataFrame(problem_orders, 
                                        columns=['id', 
                                                'created_date', 
                                                'transaction_type',
                                                'order_id',
                                                'transaction_status',
                                                'merchant_id'])
            df_merchant = df_problem_orders.groupby('merchant_id')['order_id'].count().reset_index().rename(columns={'order_id': 'count'})
        logging.info("Database connection closed.")
        return df_problem_orders, df_merchant
    except Exception as e:
        logging.info(f"Cannot not connect to database {CONFIG['database_name']}")
        logging.error(e)

def telegram_alert(message):
    requests.post(f"https://api.telegram.org/bot{CONFIG['tg_api_token']}/sendMessage?chat_id={CONFIG['chat_id']}&text={message}")
    logging.info("Message into telegram channel sent.")

def prepare_telegram_alert(df_merchant):
    alert_message = f'Monitoring result by {getuser()} at {datetime.now()}: \n'
    if not df_merchant.empty:
        for index, row in df_merchant.iterrows():
            alert_message += f"    Merchant {row['merchant_id']} has {row['count']} incomplete order{'s' if row['count']!=1 else ''} within 7 days since success <auth> transaction. \n"
    else:
        alert_message += "    There is no incomplete orders within 7 days since success <auth> transaction."
    return alert_message

def update_spreadsheet(df):
    wsh = None
    try:
        gc = gspread.service_account(filename=CONFIG['google_sa_credentials'])
        sh = gc.open(CONFIG['google_spreadsheet_name'])
        wsh = sh.worksheet(CONFIG['google_sheet_name'])
    except Exception as e:
        logging.info(f"Problems with access to shared google spreadsheet. Please contact {CONFIG['contact']}.")
        logging.error(e)
    if wsh:
        wsh.clear()
        wsh.update([df.columns.values.tolist()] + df.values.tolist())
        logging.info(f"Google sheet {CONFIG['google_spreadsheet_name']} updated.")

def run_monitoring():
    warnings.filterwarnings("ignore")

    logging.info("Monitoring started.")
    if os.path.exists(CONFIG['database_name']):
        df_gsheet, df_tg = get_not_incomplete_orders()
    
        telegram_alert(prepare_telegram_alert(df_tg))
        update_spreadsheet(df_gsheet)
    else:
        logging.warning(f"Database `{CONFIG['database_name']}` was not found. Make sure you have already created database.")
    logging.info("Monitoring finished.")