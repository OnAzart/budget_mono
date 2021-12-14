from random import randint
from traceback import format_exc, print_exc
from time import sleep
from telebot import TeleBot

from steps_in_bot import *
from data import *

config = take_creds()
TOKEN = config['TG']['test_token']
bot = TeleBot(TOKEN)
data = Data()

today = datetime.now().strftime('%d %B %Y')


@bot.message_handler(commands=['start'])
def start(message):
    user = UserTools(name=message.from_user.first_name, nickname=message.from_user.username, chat_id=message.chat.id)
    msg1 = f"Привіт!) Ти в простому непростому світі, де потрібно слідкувати за всілякими речима.\n" \
           f"Я зможу допомагати тобі в веденні бюджету і щоденно відсилати статистику витрат з Монобанку."
    bot.send_message(user.user_db.chat_id, msg1)

    bot.send_chat_action(user.user_db.chat_id, 'typing')
    sleep(randint(1, 3))
    if not user.is_profile_filled:
        poll = ProfilePoll(bot, user)
    else:
        bot.send_message(text='Вибирай що хочеш дізнатись', chat_id=user.user_db.chat_id, reply_markup=main_markup)  #


@bot.message_handler(content_types=['text'])
def process_text(message):
    cid = message.chat.id
    user = UserTools(chat_id=message.chat.id)
    mono = user.mono

    bot.send_chat_action(cid, 'typing')
    sleep(randint(1, 3))

    msg = message.text

    print(user.user_db.name, ": ", msg)
    try:
        mess_to_send = ''
        for key, keyboard_item in keyboard_dict.items():
            if msg == key:
                if keyboard_item.get('unit', None):
                    res = mono.statistic_for_period(unit=keyboard_item['unit'], sign='-')
                    mess_to_send = answer_pattern.format(time_unit=keyboard_item['ukr_str'],
                                                         negative_spends=res.get('negative'),
                                                         negative_pocket_spends=res.get("negative_pocket"),
                                                         negative_major_spends=res.get("negative_major"))
                elif msg == 'Профіль':
                    # fill_profile(bot, cid)
                    mess_to_send = ''
                break
        else:
            mess_to_send = "Такої команди не існує."
        bot.send_message(cid, mess_to_send)
    except Exception as e:
        print(format_exc())
        bot.send_message(cid, 'Зачекай хвилину перед тим як робити запит')
        bot.send_chat_action(cid, 'typing')
        sleep(60)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print("ERROR. Seems like u need to fix it( ")
        print(format_exc())
        sleep(3)
        bot.polling(none_stop=True)
        bot.send_message(549537340, format_exc())
