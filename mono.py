import json
from pprint import pprint
import requests
from os import getcwd
import pandas as pd
from additional_tools import *

working_directory = '/home/ubuntu/projects/budget_mono' if not 'nazartutyn' in getcwd() \
    else '/Users/nazartutyn/PycharmProjects/budget_mono'


class MonobankApi:
    def __init__(self, token):
        self.token = token

    def take_personal_info(self):
        url = 'https://api.monobank.ua/personal/client-info'
        headers = {'X-Token': self.token}
        resp = requests.get(url=url, headers=headers)
        resp = resp.json()
        pprint(resp)
        return resp

    def take_payments(self, from_: str = take_start_of_dateunit('week'), account='0') -> dict:
        """ Taking payments for certain date unit."""
        now = str(int(take_now().timestamp()))
          # account of user

        url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
        headers = {'X-Token': self.token,
                   'account': '0',
                   'from': from_}

        resp = requests.get(url=url, headers=headers)
        payments_dict = resp.json()
        self._add_categories(payments_dict)
        # pprint(payments_dict)
        return payments_dict

    def _add_categories(self, payments_dict):
        categories = json.load(open(join(working_directory, 'categories.json'), 'r'))
        wider_categories = json.load(open(join(working_directory, 'wider_categories.json'), 'r'))
        for payment in payments_dict:
            try:
                mcc = payment['mcc']
                for category in categories:
                    if mcc in category['mcc']:
                        payment['category'] = category['name']
                        print(payment['description'], payment['category'])

                for wider_category in wider_categories:
                    if str(mcc) in wider_category['mcc']:
                        payment['wider_category'] = wider_category['shortDescription']
                        print(payment['description'], payment['wider_category'])
            except Exception:
                print(payment)
                continue

    def _divide_spends_by_amount(self, negative_list: list) -> tuple:
        """ Divide spends to major spendings (more that 200 uah) and pocket spends."""
        paym_pocket_money_dict = [el for el in negative_list if abs(el['amount']) <= 200 * 100]
        paym_major_money_dict = [el for el in negative_list if abs(el['amount']) > 200 * 100]  # more that 200 uah
        pocket_money_df = pd.DataFrame(paym_pocket_money_dict)
        major_money_df = pd.DataFrame(paym_major_money_dict)

        pocket_sum = pocket_money_df.amount.sum() / 100 if not pocket_money_df.empty else 0
        major_sum = major_money_df.amount.sum() / 100 if not major_money_df.empty else 0
        return str(pocket_sum), str(major_sum)

    def _filter_payments(self, paym_dict: dict, banka: bool = True, limit: int = 0) -> dict:
        """ Getting rid of transfers with banka and other filters """
        if banka:
            paym_dict = [el for el in paym_dict if 'банки' not in el['description']]
        if limit:
            paym_dict = [el for el in paym_dict if abs(el['amount']) <= limit * 100]
        return paym_dict

    def statistic_for_period(self, sign: str = ' ', unit: str = 'today', account_id: str = '0', limit: int = 0) -> dict:
        """ Return statistic for certain period."""
        start_at_timestamp = take_start_of_dateunit(unit=unit)
        payments_list = self.take_payments(start_at_timestamp, account=account_id)
        if isinstance(payments_list, dict):
            print(payments_list)
            error_message = payments_list['error_description']
            raise ValueError(error_message)
        result_sum = {}

        payments_list = self._filter_payments(payments_list, banka=True, limit=limit)
        # pprint(payments_list)

        if '+' in sign:
            payments_dict_plus = [el for el in payments_list if el['amount'] > 0]
            pay_df = pd.DataFrame(payments_dict_plus)
            if not pay_df.empty:
                result_sum['positive'] = float(str(pay_df.amount.sum() / 100))

            else:
                result_sum['positive'] = 0

        if '-' in sign:
            payments_dict_minus = [el for el in payments_list if el['amount'] < 0]
            pay_df = pd.DataFrame(payments_dict_minus)
            if not pay_df.empty:
                result_sum['negative'] = float(str(pay_df.amount.sum() / 100))

                pocket_spends, major_spends = self._divide_spends_by_amount(payments_dict_minus)
                result_sum['negative_pocket'] = float(pocket_spends) if pocket_spends else 0
                result_sum['negative_major'] = float(major_spends) if major_spends else 0
            else:
                result_sum['negative'] = 0

        pay_df = pd.DataFrame(payments_list)
        if not pay_df.empty:
            result_sum['general'] = pay_df.amount.sum() / 100
        else:
            result_sum['general'] = 0

        # print(pay_df[['amount']].describe())
        print(result_sum)
        return result_sum


# if it called directly
if __name__ == '__main__':
    mono = MonobankApi(token='uI86nMW0QUfLpztN-089F1kO8Ui36xez7XonaqX-RJBg')
    # mono.take_personal_info()
    mono.statistic_for_period()
    # spent_week = mono.statistic_for_period(sign='+-', unit='week')
    # print(spent_week)
