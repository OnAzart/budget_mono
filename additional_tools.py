from configparser import ConfigParser
from datetime import datetime, timedelta
from os import getcwd
from os.path import expanduser, join

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# GLOBAL VARIABLES USED IN PROJECT
keyboard_list = ['За сьогодні', 'За тиждень', 'За місяць', 'Профіль']
main_markup = ReplyKeyboardMarkup(resize_keyboard=True)

but1 = KeyboardButton(keyboard_list[0])
but2 = KeyboardButton(keyboard_list[1])
but3 = KeyboardButton(keyboard_list[2])
but4 = KeyboardButton(keyboard_list[3])

main_markup.add(but1, but2)
main_markup.add(but3, but4)


def take_now() -> datetime:
    if 'nazartutyn' in getcwd():
        hours_delta = 0
    else:
        hours_delta = 3
    return datetime.now() + timedelta(hours=hours_delta)


def take_start_of_dateunit(unit: str = 'today') -> str:
    today = take_now()
    if unit == 'today':
        this_day_start = datetime(year=today.year, month=today.month,
                                  day=today.day, hour=0, second=0)
        print(this_day_start)
        return str(int(this_day_start.timestamp()))
    elif unit == 'week':
        this_week_start = datetime(year=today.year, month=today.month,
                                   day=(today - timedelta(today.weekday())).day)
        print(this_week_start)
        return str(int(this_week_start.timestamp()))
    elif unit == 'month':
        this_month_start = datetime(year=today.year, month=today.month, day=1)
        print(this_month_start)
        return str(int(this_month_start.timestamp()))


def take_creds() -> ConfigParser:
    if 'nazar' in expanduser('~'):
        main_path = '/Users/nazartutyn/PycharmProjects/budget_mono'
    else:
        main_path = expanduser('~') + '/projects/budget_mono'
    config = ConfigParser()
    config.read(join(main_path, 'tokens.ini'))
    return config
