from math import ceil
from pprint import pprint
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from additional_tools import *


def take_payments(from_=take_start_of_date('week'), token='uI86nMW0QUfLpztN-089F1kO8Ui36xez7XonaqX-RJBg'):
    today = take_now()
    now = str(int(today.timestamp()))
    account = '0'

    url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
    headers = {'X-Token': token,
               'account': '0',
               'from': from_}

    resp = requests.get(url=url, headers=headers)
    payments_dict = resp.json()
    return payments_dict


def statistic_for_period(sign: str = ' ', unit='today', token: str = 'uI86nMW0QUfLpztN-089F1kO8Ui36xez7XonaqX-RJBg'):
    start_at_timestamp = take_start_of_date(unit=unit)
    payments_dict = take_payments(start_at_timestamp, token=token)

    # getting rid of transfers with banka
    payments_dict = [el for el in payments_dict if 'банки' not in el['description']]
    # pprint(payments_dict)

    if sign == '+':
        payments_dict = [el for el in payments_dict if el['amount'] >= 0]
    elif sign == '-':
        payments_dict = [el for el in payments_dict if el['amount'] < 0]

    pay_df = pd.DataFrame(payments_dict)
    if pay_df.empty:
        return '0'

    spent_amount_day = ceil(pay_df.amount.sum() / 100)
    print(spent_amount_day)
    # print(pay_df[['amount']].describe())
    return str(spent_amount_day)


if __name__ == '__main__':
    spent_day = statistic_for_period(unit='today')
    spent_week = statistic_for_period(unit='week')
    # spent_week = statistic_for_week()
