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
    positive_sum_today = statistic_for_period(unit='today', sign='+')
    negative_sum_today = statistic_for_period(unit='today', sign='-')
    together_sum_today = str(int(positive_sum_today) + int(negative_sum_today))
    sum_week = statistic_for_period(unit='week')

    mess_to_send = f'''💰 {'+' if int(together_sum_today)>0 else ''}{together_sum_today} за сьогодні 💰
            Витрати: {negative_sum_today} грн 
            Надходження: {positive_sum_today} грн
            
            Загалом цього тижня: {sum_week} грн'''
    bot.send_message(chat_id, mess_to_send, parse_mode='html')


try:
    users = retrieve_users_from_db()
    for user in users:
        send_group_statistic(user.chat_id)
    print(f'Відправлено статистику для {len(users)}.')
except:
    print('Retry...')
    sleep(60)
    send_group_statistic()

# send big spends separately
