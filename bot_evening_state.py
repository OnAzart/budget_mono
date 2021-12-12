#!/usr/bin/env python
from time import sleep
from traceback import format_exc

import telebot

from additional_tools import take_creds
from data import retrieve_users_from_db, Data, update_user_send_time
from mono import statistic_for_period


config = take_creds()

TOKEN = config['TG']['token']
bot = telebot.TeleBot(TOKEN)

data = Data()


def send_group_statistic(chat_id, token):
    result_spends = statistic_for_period(unit='today', sign='+-', token=token)
    sleep(10)
    # together_sum_today = str(int(float(positive_sum_today) + float(negative_sum_today)))
    result_spends_week = statistic_for_period(unit='week', token=token)

    mess_to_send = f"💰 {'+' if int(float(result_spends['general'])) > 0 else ''}{result_spends['general']} " \
                   f"грн за сьогодні 💰" \
                   f"\nКишенькові Витрати: {result_spends.get('negative_pocket', 0)} грн" \
                   f"\nБільші Витрати: {result_spends.get('negative_major',0)} грн" \
                   f"\nНадходження: {result_spends.get('positive')} грн" \
                   f"\n\nЗагалом цього тижня: {result_spends_week.get('general')} грн"
    bot.send_message(chat_id, mess_to_send, parse_mode='html')


def main():
    users = retrieve_users_from_db()
    for i in range(len(users)):
        cid = users[i].chat_id
        mono_token = users[i].monobank_token
        print(users[i].name, cid)
        send_group_statistic(cid, mono_token)
        update_user_send_time(cid)
        sleep(60)
    print(f'Відправлено статистику для {len(users)}.')
    # send big spends separately


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Retry... {format_exc()}')
        bot.send_message(chat_id=549537340, text=f"{format_exc()}")
        sleep(60)
        main()
