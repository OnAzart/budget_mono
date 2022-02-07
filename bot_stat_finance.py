from random import randint
from traceback import format_exc, print_exc
from time import sleep
from telebot import TeleBot

from steps_in_bot import *
from data import *

config = take_creds()
TOKEN = config['TG']['token']
bot = TeleBot(TOKEN)
data = Data()

today = datetime.now().strftime('%d %B %Y')


@bot.message_handler(commands=['start'])
def start(message):
    user = UserTools(name=message.from_user.first_name, nickname=message.from_user.username, chat_id=message.chat.id)
    msg1 = """Гроші постійно кудись незрозуміло відлітають 💸
Давай я допоможу тобі відслідковувати їх."""
    bot.send_message(user.user_db.chat_id, msg1)

    bot.send_chat_action(user.user_db.chat_id, 'typing')
    sleep(randint(1, 2))

    if not user.is_profile_filled or True:
        ProfilePoll(bot, user)
    else:
        bot.send_message(text='Статистику за який період часу ти хочеш дізнатись?', chat_id=user.user_db.chat_id,
                         reply_markup=main_markup)


@bot.message_handler(content_types=['text'])
def process_text(message):
    cid = message.chat.id
    user = UserTools(chat_id=message.chat.id)
    mono = user.mono

    bot.send_chat_action(cid, 'typing')
    # sleep(randint(1, 2))
    msg = message.text
    print(user.user_db.name, ": ", msg)
    try:
        mess_to_send = ''
        for key, keyboard_item in keyboard_dict.items():
            if msg == key:
                if keyboard_item.get('unit', None):
                    mess_to_send = collect_statistic(keyboard_item, cid, mono)
                    bot.send_message(cid, mess_to_send, parse_mode='html')
                elif msg == 'Профіль':
                    # fill_profile(bot, cid)
                    # mess_to_send = 'Тут ти маєш змогу змінити свої налаштування профілю.'
                    mess_to_send = collect_profile_description(user.user_db)
                    bot.send_message(cid, mess_to_send, reply_markup=form_profile_markup(user.user_db)[0])
                break
        else:
            mess_to_send = "Такої команди не існує."

        profile_markup, profile_buttons = form_profile_markup(user.user_db)
        if msg == profile_buttons[0]:  # cards
            choose_card(bot=bot, chat_id=cid, proceed=False)
        elif msg == profile_buttons[1]:
            user.change_need_evening_push()
            profile_markup, profile_buttons = form_profile_markup(user.user_db)
            bot.send_message(chat_id=cid, text="Параметри розсилки змінені.", reply_markup=profile_markup)
        elif msg == profile_buttons[2]:
            do_need_a_value_limit(bot, cid)
        elif msg == profile_buttons[-1]:
            mess_to_send = 'Статистику за який період часу ти хочеш дізнатись?'
            bot.send_message(cid, mess_to_send, reply_markup=main_markup)
        elif mess_to_send == "Такої команди не існує.":
            bot.send_message(cid, mess_to_send, reply_markup=main_markup, parse_mode='html')
    except ValueError as ve:
        print(format_exc(ve))
        bot.send_chat_action(cid, 'typing')
        sleep(3)
        bot.send_message(cid, 'Не поспішай. Повтори запит через 1 хв. Друг mono не дозволяє частіше)')
    except Exception as e:
        print(format_exc(e))
        bot.send_chat_action(cid, 'typing')
        sleep(3)
        bot.send_message(cid, 'Упс, спробуй через хвилину. Входжу в тонус 👽')


@bot.callback_query_handler(lambda call: True)
def process_callback(call):
    area, action, data = call.data.split(';')
    user = UserTools(chat_id=call.message.chat.id)
    if area == 'card':
        if action == 'change':
            change_activity_of_card(data)
            choose_card(bot=bot, call=call)
        elif action == 'done':
            if data == 'proceed':
                do_need_an_evening_push(bot=bot,  cid=user.user_db.chat_id)
            else:
                finish_stage(bot, call.message.chat.id)
            return True
    elif area == 'push':
        value = True if action == 'yes' else False
        user.change_need_evening_push(value)
        do_need_a_value_limit(bot=bot,  cid=user.user_db.chat_id)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print("ERROR. Seems like u need to fix it( ")
        print(format_exc())
        sleep(30)
        bot.polling(none_stop=True)
        bot.send_message(549537340, format_exc())
