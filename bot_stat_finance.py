from datetime import datetime
from copy import deepcopy
from random import randint
from traceback import format_exc
from time import sleep

from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardRemove, InputMediaDocument

from additional_tools import main_markup, keyboard_dict, collect_profile_description, form_profile_markup, take_creds
from steps_in_bot import ProfilePoll, collect_statistic, choose_card, \
    do_need_a_value_limit, do_need_an_evening_push, finish_stage, form_file_to_export
from data import UserTools, change_activity_of_card
from plot.plots import Plots

config = take_creds()
TOKEN = config['TG']['token']
bot = TeleBot(TOKEN)

today = datetime.now().strftime('%d %B %Y')


@bot.message_handler(commands=['start'])
def start(message):
    user = UserTools(name=message.from_user.first_name, nickname=message.from_user.username, chat_id=message.chat.id)

    msg1 = """Гроші постійно кудись незрозуміло відлітають 💸
Давай я допоможу тобі відслідковувати їх."""
    bot.send_message(user.user_db.chat_id, msg1)
    bot.send_chat_action(user.user_db.chat_id, 'typing')
    sleep(randint(1, 2))

    if not user.is_profile_filled or True:  # True means everytime
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
    msg = message.text
    print(user.user_db.name, ": ", msg)

    # will be rewritten if further condition not approve
    mess_to_send = "Такої команди не існує."
    try:
        # MAIN MENU BUTTONS CHECK
        for key, keyboard_item in keyboard_dict.items():
            if msg == key:
                if keyboard_item.get('unit', None):
                    if user.is_minute_since_activity_passed():
                        mess_to_send, callback_details = collect_statistic(keyboard_item, cid, mono)
                        details_but = InlineKeyboardButton(text='Детальніше', callback_data=str(callback_details))

                        callback_export = deepcopy(callback_details)
                        callback_export.area = 'export'
                        export_but = InlineKeyboardButton(text='Завантажити витрати', callback_data=str(callback_export))

                        details_markup = InlineKeyboardMarkup()
                        details_markup.add(details_but)
                        details_markup.add(export_but)

                        bot.send_message(cid, mess_to_send, parse_mode='html', reply_markup=details_markup)
                        user.update_user_send_time()
                    else:
                        mess_to_send = 'Спробуй ще раз через хвилину;)'
                        bot.send_message(cid, mess_to_send)
                elif msg == 'Профіль':
                    # fill_profile(bot, cid)
                    # mess_to_send = 'Тут ти маєш змогу змінити свої налаштування профілю.'
                    mess_to_send = collect_profile_description(user.user_db)
                    bot.send_message(cid, mess_to_send, reply_markup=form_profile_markup(user.user_db)[0])
                break

        # PROFILE BUTTONS CHECK
        if mess_to_send == "Такої команди не існує.":
            profile_markup, profile_buttons = form_profile_markup(user.user_db)
            if msg == profile_buttons[0]:
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
    """ callback = area; action; data; day_unit """
    print(call.data)
    area, action, data, day_unit = call.data.split(';')
    user = UserTools(chat_id=call.message.chat.id)
    if area == 'card':  # change activeness of cards
        if action == 'change':
            change_activity_of_card(data)
            choose_card(bot=bot, call=call)
        elif action == 'done':
            if data == 'proceed':
                do_need_an_evening_push(bot=bot,  cid=user.user_db.chat_id)
            else:
                finish_stage(bot, call.message.chat.id)
            return True
    elif area == 'push':  # change evening push settings
        value = action == 'yes'
        user.change_need_evening_push(value)
        do_need_a_value_limit(bot=bot,  cid=user.user_db.chat_id)
    elif area == 'details':  # detailed statistic
        # cid, from_tmsp, to_tsmp = data.split('-')
        print(data)

        list_of_paths_to_images = Plots(redis_token=data, category=True, area_plot=day_unit, weekday_to_time=True).get_plots_paths()
        media = [InputMediaPhoto(open(image, 'rb')) for image in list_of_paths_to_images]
        bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id,
                                      reply_markup=InlineKeyboardMarkup())
        bot.send_media_group(media=media, chat_id=call.message.\
                             chat.id, reply_to_message_id=call.message.id)
    elif area == 'export':
        file_to_send = form_file_to_export(redis_token=data, day_unit=day_unit)
        # bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id,
        #                               reply_markup=InlineKeyboardMarkup())
        bot.send_document(chat_id=call.message.chat.id, document=open(file_to_send, 'rb'),
                          reply_to_message_id=call.message.id)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            print(format_exc())
            try:
                # bot.send_message(549537340, format_exc())
                bot.stop_bot()
            except:
                print("Bot is probably already stopped.")
            print("ERROR. RELOADING.. Seems like u need to fix it( ")
            sleep(3)
            bot = TeleBot(TOKEN)
