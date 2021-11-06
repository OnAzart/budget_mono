#!/usr/bin/env python
from configparser import ConfigParser
from time import sleep
from datetime import datetime, timedelta
from traceback import format_exc

import telebot
from mono import statistic_for_period
from data import retrieve_users_from_db, Data, update_user_send_time

config = ConfigParser()
config.read('tokens.ini')

TOKEN = config['TG']['token']
chat_id = 549537340
bot = telebot.TeleBot(TOKEN)

data = Data()


def send_group_statistic(chat_id):
    result_spends = statistic_for_period(unit='today', sign='+-')
    # positive_sum_today, negative_sum_today = result_spends['positive']
    # negative_sum_today = statistic_for_period(unit='today', sign='-')
    sleep(10)
    # together_sum_today = str(int(float(positive_sum_today) + float(negative_sum_today)))
    result_spends_week = statistic_for_period(unit='week')

    mess_to_send = f"💰 {'+' if int(float(result_spends['general'])) > 0 else ''}{result_spends['general']} грн за сьогодні 💰" \
                   f"\nКишенькові Витрати: {result_spends['negative_pocket']} грн" \
                   f"\nБільші Витрати: {result_spends['negative_major']} грн" \
                   f"\nНадходження: {result_spends['positive']} грн" \
                   f"\n\nЗагалом цього тижня: {result_spends_week['general']} грн"
    bot.send_message(chat_id, mess_to_send, parse_mode='html')


def main():
    users = retrieve_users_from_db()
    for i in range(len(users)):
        cid = users[i].chat_id  # 549537340
        print(users[i].name, cid)
        send_group_statistic(cid)
        update_user_send_time(cid)
        sleep(60)
    print(f'Відправлено статистику для {len(users)}.')
    # send big spends separately


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Retry... {format_exc()}')
        sleep(60)
        main()
