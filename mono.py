from math import ceil
from pprint import pprint
import requests
from datetime import datetime, timedelta
import pandas as pd


def take_payments(from_):
    now = str(int(datetime.now().timestamp()))
    account = '0'

    url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
    headers = {'X-Token': 'uI86nMW0QUfLpztN-089F1kO8Ui36xez7XonaqX-RJBg',
               'account': '0',
               'from': from_}

    resp = requests.get(url=url, headers=headers)
    payments_dict = resp.json()
    # pprint(payments_dict)
    return payments_dict


def statistic_for_today():
    last_day_start = datetime(year=datetime.today().year, month=datetime.today().month,
                              day=datetime.today().day, hour=0, second=0)
    print(last_day_start)
    last_day_start_timestamp = str(int(last_day_start.timestamp()))

    payments_dict = take_payments(last_day_start_timestamp)
    pay_df = pd.DataFrame(payments_dict)
    spent_amount_day = ceil(pay_df.amount.sum() / 100)
    print(spent_amount_day)
    # print(pay_df[['amount']].describe())
    return str(spent_amount_day)


def statistic_for_week():
    last_week_start = datetime(year=datetime.today().year, month=datetime.today().month,
                               day=(datetime.today() - timedelta(datetime.today().weekday())).day)
    # last_week_start = datetime.now() - timedelta(datetime.today().weekday()) - timedelta(hours=datetime.today().hour)
    print(last_week_start)
    last_week_start_timestamp = str(int(last_week_start.timestamp()))
    payments_dict = take_payments(last_week_start_timestamp)

    pay_df = pd.DataFrame(payments_dict)
    spent_amount_week = ceil(pay_df.amount.sum() / 100)
    print(spent_amount_week)
    return str(spent_amount_week)


if __name__ == '__main__':
    spent_day = statistic_for_today()
    spent_week = statistic_for_week()
