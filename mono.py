from math import ceil
from pprint import pprint
import requests
from datetime import datetime, timedelta
import pandas as pd
import os


def take_now():
    if 'nazartutyn' in os.getcwd():
        hours_delta = 0
    else:
        hours_delta = 3
    return datetime.now() + timedelta(hours=hours_delta)


def take_payments(from_):
    today = take_now()
    now = str(int(today.timestamp()))
    account = '0'

    url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
    headers = {'X-Token': 'uI86nMW0QUfLpztN-089F1kO8Ui36xez7XonaqX-RJBg',
               'account': '0',
               'from': from_}

    resp = requests.get(url=url, headers=headers)
    payments_dict = resp.json()
    return payments_dict


def statistic_for_today():
    today = take_now()
    this_day_start = datetime(year=today.year, month=today.month,
                              day=today.day, hour=0, second=0)
    print(this_day_start)
    last_day_start_timestamp = str(int(this_day_start.timestamp()))

    payments_dict = take_payments(last_day_start_timestamp)
    payments_dict = [el for el in payments_dict if 'банки' not in el['description']]
    # pprint(payments_dict)

    pay_df = pd.DataFrame(payments_dict)
    spent_amount_day = ceil(pay_df.amount.sum() / 100)
    print(spent_amount_day)
    # print(pay_df[['amount']].describe())
    return str(spent_amount_day)


def statistic_for_week():
    today = take_now()
    this_week_start = datetime(year=today.year, month=today.month,
                               day=(today - timedelta(datetime.today().weekday())).day)
    # last_week_start = datetime.now() - timedelta(datetime.today().weekday()) - timedelta(hours=datetime.today().hour)
    print(this_week_start)
    this_week_start_timestamp = str(int(this_week_start.timestamp()))
    payments_dict = take_payments(this_week_start_timestamp)

    pay_df = pd.DataFrame(payments_dict)
    spent_amount_week = ceil(pay_df.amount.sum() / 100)
    print(spent_amount_week)
    return str(spent_amount_week)


if __name__ == '__main__':
    spent_day = statistic_for_today()
    spent_week = statistic_for_week()
