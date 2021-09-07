from datetime import datetime
from time import sleep
from traceback import format_exc

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telebot import TeleBot

from mono import statistic_for_today, statistic_for_week


TOKEN = '1959713887:AAH0idwY9L-QHPiAV-8n3xMsgeHKJWCaEf4'
bot = TeleBot(TOKEN)

keyboard_list = ['Статистика за день', 'Статистика за тиждень']
main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
but1 = KeyboardButton(keyboard_list[0])
but2 = KeyboardButton(keyboard_list[1])
main_markup.add(but1, but2)

today = datetime.now().strftime('%d %B %Y')


@bot.message_handler(commands=['start'])
def start(message):
    msg = f"Привіт!)"

    bot.send_message(message.chat.id, msg, reply_markup=main_markup)
    # print(message.chat.id, message.user.nickname)


@bot.message_handler(content_types=['text'])
def process_text(message):
    msg = message.text
    print(msg)
    if msg == keyboard_list[0]:
        sum_today = statistic_for_today()
        mess_to_send = f'Сьогодні ти витратив {sum_today} грн на якусь дурню.'
    elif msg == keyboard_list[1]:
        sum_week = statistic_for_week()
        mess_to_send = f'Цього тижня ти витратив {sum_week} грн на якусь дурню.'
    else:
        return 0
    bot.send_message(message.chat.id, mess_to_send)


def send_group_statistic():
    sum_today = statistic_for_today()
    sum_week = statistic_for_week()

    mess_to_send = f'''💰 {today} 💰
            Сьогодні: {sum_today} грн
            Цього тижня: {sum_week} грн'''
    bot.send_message(549537340, mess_to_send)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print("ERROR BLIAT")
        print(format_exc())
        sleep(3)
        bot.polling(none_stop=True)
        bot.send_message(549537340, format_exc())