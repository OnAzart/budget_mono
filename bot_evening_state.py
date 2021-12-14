#!/usr/bin/env python
from time import sleep
from traceback import format_exc

import telebot

from additional_tools import take_creds
from data import retrieve_all_users_from_db, Data, UserTools
from mono import MonobankApi


config = take_creds()

TOKEN = config['TG']['token']
bot = telebot.TeleBot(TOKEN)

data = Data()


def send_group_statistic(user):
    mono = user.mono
    result_spends = mono.statistic_for_period(unit='today', sign='+-')
    sleep(10)
    # together_sum_today = str(int(float(positive_sum_today) + float(negative_sum_today)))
    result_spends_week = mono.statistic_for_period(unit='week')

    mess_to_send = f"💰 {'+' if int(float(result_spends['general'])) > 0 else ''}{result_spends['general']} " \
                   f"грн за сьогодні 💰" \
                   f"\nКишенькові Витрати: {result_spends.get('negative_pocket', 0)} грн" \
                   f"\nБільші Витрати: {result_spends.get('negative_major',0)} грн" \
                   f"\nНадходження: {result_spends.get('positive')} грн" \
                   f"\n\nЗагалом цього тижня: {result_spends_week.get('general')} грн"
    bot.send_message(user.user_db.chat_id, mess_to_send, parse_mode='html')


def main():
    users = retrieve_all_users_from_db()
    for i in range(len(users)):
        user_tool = UserTools(user=users[i])
        send_group_statistic(user_tool)
        user_tool.update_user_send_time()
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
