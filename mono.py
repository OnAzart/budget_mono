from pprint import pprint
from traceback import print_exc

import requests
from os import getcwd
import pandas as pd

from additional_tools import take_now, take_start_of_dateunit

working_directory = '/home/azureuser/projects/budget_mono' if not 'nazartutyn' in getcwd() \
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

    def take_payments(self, from_: str = take_start_of_dateunit('week'),
                      to_=str(int(take_now().timestamp())),
                      account='0') -> dict:
        """ Taking payments for certain date unit."""

        url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{to_}'
        headers = {'X-Token': self.token,
                   'account': '0',
                   'from': from_}

        resp = requests.get(url=url, headers=headers)
        payments_dict = resp.json()
        self._add_categories(payments_dict)
        pprint(payments_dict)
        return payments_dict

    def _add_categories(self, payments_dict):
        from data import Category
        for payment in payments_dict:
            try:
                mcc = payment['mcc']
                wider_category = Category.objects.filter(mcc=mcc)
                if wider_category:
                    wider_category = wider_category[0]
                    payment['category'] = wider_category['description']
                    payment['wider_category'] = wider_category['shortDescription']
                else:
                    payment['category'] = None
                    payment['wider_category'] = None
            except Exception as e:
                print_exc()
                print('problem in :', payment)
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

    def statistic_for_period(self, sign: str = ' ', unit: str = 'today', account_id: str = '0', limit: int = 0,
                             from_: str = '', to_: str = ''):
        """ Return statistic for certain period."""
        if not all([from_, to_]):
            result_sum = {'start_timestamp': take_start_of_dateunit(unit=unit),
                          'end_timestamp': str(int(take_now().timestamp()))}
        else:
            result_sum = {'start_timestamp': from_,
                          'end_timestamp': to_}
        payments_list = self.take_payments(from_=result_sum['start_timestamp'],
                                           to_=result_sum['end_timestamp'],
                                           account=account_id)
        if isinstance(payments_list, dict):
            print(payments_list)
            error_message = payments_list['error_description']
            raise ValueError(error_message)

        payments_list = self._filter_payments(payments_list, banka=True, limit=limit)
        list(map(lambda payment: payment.update({'account_id': account_id}), payments_list))
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
        return result_sum, payments_list


# if it called directly
if __name__ == '__main__':
    mono = MonobankApi(token='')
    # mono.take_personal_info()
    mono.statistic_for_period()
    # spent_week = mono.statistic_for_period(sign='+-', unit='week')
    # print(spent_week)
