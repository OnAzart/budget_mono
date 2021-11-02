from random import randint
from time import sleep
from traceback import format_exc
from configparser import ConfigParser

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telebot import TeleBot

from steps_in_bot import *
from data import *

config = ConfigParser()
config.read('tokens.ini')

TOKEN = config['TG']['token']
bot = TeleBot(TOKEN)
data = Data()

today = datetime.now().strftime('%d %B %Y')


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    user = handle_user(name=message.from_user.first_name, nickname=message.from_user.username, chat_id=message.chat.id)

    msg1 = f"Привіт!) Ти в простому непростому світі, де потрібно слідкувати за всілякими речима." \
           f"Я зможу допомагати тобі в веденні бюджету і відсилати статистику витрат з Монобанку."
    bot.send_message(cid, msg1)

    bot.send_chat_action(cid, 'typing')
    sleep(randint(1, 3))
    fill_profile(bot, cid)

    # print(message.chat.id, message.user.nickname)


@bot.message_handler(content_types=['text'])
def process_text(message):
    cid = message.chat.id
    user = User.objects.filter(chat_id=cid)[0]
    token = user.monobank_token

    msg = message.text
    print(msg)
    try:
        if msg == keyboard_list[0]:
            sum_today = statistic_for_period(unit='today', sign='-', token=token)[0]
            mess_to_send = f'Сьогодні ти витратив {sum_today} грн на якусь дурню.'
        elif msg == keyboard_list[1]:
            sum_week = statistic_for_period(unit='week', sign='-', token=token)[0]
            mess_to_send = f'Цього тижня ти витратив {sum_week} грн на якусь дурню.'
        elif msg == keyboard_list[2]:
            sum_month = statistic_for_period(unit='month', sign='-', token=token)[0]
            mess_to_send = f'Цього місяця ти витратив {sum_month} грн на якусь дурню.'
        elif msg == keyboard_list[3]:
            fill_profile(bot, cid)
            mess_to_send = ''
        else:
            mess_to_send = "Такої команди не існує."
        bot.send_message(cid, mess_to_send)
    except:
        bot.send_message(cid, 'Зачекай хвилину перед тим як робити запит')
        sleep(60)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print("ERROR BLIAT")
        print(format_exc())
        sleep(3)
        bot.polling(none_stop=True)
        bot.send_message(549537340, format_exc())