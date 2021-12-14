from pprint import pprint
import requests
import pandas as pd
from additional_tools import *


class MonobankApi:
    def __init__(self, token):
        self.token = token

    def take_payments(self, from_: str = take_start_of_dateunit('week')) -> dict:
        """ Taking payments for certain date unit."""
        now = str(int(take_now().timestamp()))
        account = '0'  # account of user

        url = f'https://api.monobank.ua/personal/statement/{account}/{from_}/{now}'
        headers = {'X-Token': self.token,
                   'account': '0',
                   'from': from_}

        resp = requests.get(url=url, headers=headers)
        payments_dict = resp.json()
        pprint(payments_dict)
        return payments_dict

    def _divide_spends_by_amount(self, negative_list: list) -> tuple:
        """ Divide spends to major spendings (more that 200 uah) and pocket spends."""
        paym_pocket_money_dict = [el for el in negative_list if abs(el['amount']) <= 200 * 100]
        paym_major_money_dict = [el for el in negative_list if abs(el['amount']) > 200 * 100]  # more that 200 uah
        pocket_money_df = pd.DataFrame(paym_pocket_money_dict)
        major_money_df = pd.DataFrame(paym_major_money_dict)

        pocket_sum = pocket_money_df.amount.sum() / 100 if not pocket_money_df.empty else 0
        major_sum = major_money_df.amount.sum() / 100 if not major_money_df.empty else 0
        return str(pocket_sum), str(major_sum)

    def _filter_payments(self, paym_dict: dict, banka: bool = True) -> dict:
        """ Getting rid of transfers with banka """
        if banka:
            paym_dict = [el for el in paym_dict if 'банки' not in el['description']]
        return paym_dict

    def statistic_for_period(self, sign: str = ' ', unit: str = 'today') -> dict:
        """ Return statistic for certain period."""
        start_at_timestamp = take_start_of_dateunit(unit=unit)
        payments_list = self._take_payments(start_at_timestamp)
        if isinstance(payments_list, dict):
            print(payments_list)
            assert Exception("Wait")
        result_sum = {}

        payments_list = self._filter_payments(payments_list, banka=True)
        # pprint(payments_list)

        if '+' in sign:
            payments_dict_plus = [el for el in payments_list if el['amount'] > 0]
            pay_df = pd.DataFrame(payments_dict_plus)
            if not pay_df.empty:
                result_sum['positive'] = (str(pay_df.amount.sum() / 100))
            else:
                result_sum['positive'] = '0'

        if '-' in sign:
            payments_dict_minus = [el for el in payments_list if el['amount'] < 0]
            pay_df = pd.DataFrame(payments_dict_minus)
            if not pay_df.empty:
                result_sum['negative'] = (str(pay_df.amount.sum() / 100))

                pocket_spends, major_spends = self._divide_spends_by_amount(payments_dict_minus)
                result_sum['negative_pocket'] = pocket_spends
                result_sum['negative_major'] = major_spends
            else:
                result_sum['negative'] = '0'

        pay_df = pd.DataFrame(payments_list)
        if not pay_df.empty:
            result_sum['general'] = str(pay_df.amount.sum() / 100)
        else:
            result_sum['general'] = '0'

        # print(pay_df[['amount']].describe())
        print(result_sum)
        return result_sum


# if it called directly
if __name__ == '__main__':
    mono = MonobankApi(token='')
    spent_week = mono.statistic_for_period(sign='+-', unit='today')
    print(spent_week)
