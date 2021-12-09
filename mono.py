from math import ceil
from pprint import pprint
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from additional_tools import *


def take_payments(from_=take_start_of_date('week'), token: str = ''):
    today = take_now()
    now = str(int(today.timestamp()))
    account = '0'

    url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
    headers = {'X-Token': token,
               'account': '0',
               'from': from_}

    resp = requests.get(url=url, headers=headers)
    payments_dict = resp.json()
    pprint(payments_dict)
    return payments_dict


def divide_spends_by_amount(negative_dict):
    payments_dict_pocket = [el for el in negative_dict if abs(el['amount']) <= 200*100]
    payments_dict_major = [el for el in negative_dict if abs(el['amount']) > 200*100]
    pocket_df = pd.DataFrame(payments_dict_pocket)
    major_df = pd.DataFrame(payments_dict_major)

    pocket_sum = pocket_df.amount.sum() / 100 if not pocket_df.empty else 0
    major_sum = major_df.amount.sum() / 100 if not major_df.empty else 0
    return str(pocket_sum), str(major_sum)


def statistic_for_period(sign: str = ' ', unit='today', token: str = ''):
    start_at_timestamp = take_start_of_date(unit=unit)
    payments_dict = take_payments(start_at_timestamp, token=token)
    result_sum = {}

    # getting rid of transfers with banka
    payments_dict = [el for el in payments_dict if 'банки' not in el['description']]
    # pprint(payments_dict)

    if '+' in sign:
        payments_dict_plus = [el for el in payments_dict if el['amount'] > 0]
        pay_df = pd.DataFrame(payments_dict_plus)
        if not pay_df.empty:
            result_sum['positive'] = (str(pay_df.amount.sum() / 100))
        else:
            result_sum['positive'] = '0'

    if '-' in sign:
        payments_dict_minus = [el for el in payments_dict if el['amount'] < 0]
        pay_df = pd.DataFrame(payments_dict_minus)
        if not pay_df.empty:
            result_sum['negative'] = (str(pay_df.amount.sum() / 100))

            pocket_spends, major_spends = divide_spends_by_amount(payments_dict_minus)
            result_sum['negative_pocket'] = pocket_spends
            result_sum['negative_major'] = major_spends
        else:
            result_sum['negative'] = '0'

    pay_df = pd.DataFrame(payments_dict)
    if not pay_df.empty:
        result_sum['general'] = str(pay_df.amount.sum() / 100)
    else:
        result_sum['general'] = '0'


    # print(pay_df[['amount']].describe())
    print(result_sum)
    return result_sum


if __name__ == '__main__':
    # plus, minus = statistic_for_period(unit='today')
    # print(plus, minus)
    spent_week = statistic_for_period(sign='+-', unit='today')
    print(spent_week)
