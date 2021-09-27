#!/usr/bin/env python
from time import sleep
from datetime import datetime, timedelta

import telebot
from mono import statistic_for_today, statistic_for_week

TOKEN = '1959713887:AAH0idwY9L-QHPiAV-8n3xMsgeHKJWCaEf4'
chat_id = 549537340
bot = telebot.TeleBot(TOKEN)


def take_now():
    return datetime.now() + timedelta(hours=3)


def send_group_statistic():
    positive_sum_today = statistic_for_today(sign='+')
    negative_sum_today = statistic_for_today(sign='-')
    sum_week = statistic_for_week()

    mess_to_send = f'''💰 {take_now().strftime('%d %B %Y')} 💰
            *Сьогодні*:
            Витрати: {negative_sum_today} грн 
            Надходження: {positive_sum_today} грн
            
            *Цього тижня*: {sum_week} грн'''
    bot.send_message(chat_id, mess_to_send, parse_mode='html')


try:
    send_group_statistic()
except:
    print('Retry...')
    sleep(60)
    send_group_statistic()
