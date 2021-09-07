#!/usr/bin/env python
from time import sleep
from datetime import datetime

import telebot
from mono import statistic_for_today, statistic_for_week

TOKEN = '1959713887:AAH0idwY9L-QHPiAV-8n3xMsgeHKJWCaEf4'
chat_id = 549537340
bot = telebot.TeleBot(TOKEN)

today = datetime.now().strftime('%d %B %Y')


def send_group_statistic():
    sum_today = statistic_for_today()
    sum_week = statistic_for_week()

    mess_to_send = f'''💰 {today} 💰
            Сьогодні: {sum_today} грн
            Цього тижня: {sum_week} грн'''
    bot.send_message(chat_id, mess_to_send)


try:
    send_group_statistic()
except:
    sleep(60)
    send_group_statistic()
