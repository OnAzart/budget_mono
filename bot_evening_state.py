#!/usr/bin/env python
from configparser import ConfigParser
from time import sleep
from datetime import datetime, timedelta

import telebot
from mono import statistic_for_period
from data import retrieve_users_from_db, Data

config = ConfigParser()
config.read('tokens.ini')

TOKEN = config['TG']['token']
chat_id = 549537340
bot = telebot.TeleBot(TOKEN)

data = Data()


def send_group_statistic(chat_id):
    positive_sum_today, negative_sum_today = statistic_for_period(unit='today', sign='+-')
    # negative_sum_today = statistic_for_period(unit='today', sign='-')
    sleep(5)
    together_sum_today = str(int(float(positive_sum_today) + float(negative_sum_today)))
    sum_week = statistic_for_period(unit='week')[0]

    mess_to_send = f"💰 {'+' if int(together_sum_today) > 0 else ''}{together_sum_today} грн за сьогодні 💰" \
                   f"\nВитрати: {negative_sum_today} грн" \
                   f"\nНадходження: {positive_sum_today} грн" \
                   f"\n\nЗагалом цього тижня: {sum_week} грн"
    bot.send_message(chat_id, mess_to_send, parse_mode='html')


def main():
    users = retrieve_users_from_db()
    for i in range(len(users)):
        cid = users[i].chat_id
        print(users[i].name)
        send_group_statistic(cid)
        break
        sleep(60)
    print(f'Відправлено статистику для {len(users)}.')
    # send big spends separately


if __name__ == '__main__':
    try:
        main()
    except:
        print('Retry...')
        sleep(60)
        main()
