#!/usr/bin/env python
from time import sleep
from traceback import format_exc

import telebot

from additional_tools import take_creds, keyboard_dict
from data import retrieve_all_users_from_db, Data, UserTools
from mono import MonobankApi
from steps_in_bot import collect_statistic


config = take_creds()

TOKEN = config['TG']['token']
bot = telebot.TeleBot(TOKEN)

data = Data()


def send_group_statistic(user):
    mono = user.mono
    mess_to_send = collect_statistic(keyboard_item=keyboard_dict['За сьогодні'], cid=user.user_db.chat_id, mono=mono)
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
