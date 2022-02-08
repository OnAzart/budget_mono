from configparser import ConfigParser
from datetime import datetime, timedelta
from os import getcwd
from os.path import expanduser, join
from babel.dates import format_datetime

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# GLOBAL VARIABLES USED IN PROJECT

keyboard_dict = {'За сьогодні': {'unit': 'today', 'ukr_str': 'cьогодні', 'smile': '🌝'},
                 'За тиждень': {'unit': 'week', 'ukr_str': 'з початку тижня', 'smile': '🌛'},
                 'За місяць': {'unit': 'month', 'smile': '🌚',
                               'ukr_str': f'протягом {format_datetime(datetime.now(), "MMMM", locale="uk_UA")}'},
                 'Профіль': {"No functionality": "No functionality"}}

answer_pattern = '\nВитрачено: {negative_spends} грн.' \
                 '\nОтримано: {positive} грн.'


# answer_pattern = 'Цього {time_unit} ти витратив {negative_spends} грн на якусь дурню.' \
#                  '\nКишенькові: {negative_pocket_spends} грн.' \
#                  '\nБільші: {negative_major_spends} грн.'

currencies = {980: '₴',
              840: '$',
              978: '€'}

mono_inl_markup = InlineKeyboardMarkup()
mono_button = InlineKeyboardButton(text='Дізнатись токен', url='https://api.monobank.ua/')
mono_inl_markup.add(mono_button)

main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_list = list(keyboard_dict)
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
        this_week_start = today - timedelta(today.weekday())
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


def is_at_least_one_card_chosen(cards_data):
    for card in cards_data:
        if card.is_active:
            return True


def form_profile_markup(user_db):
    profile_buttons = ['Управління картками', "{} вечірню статистику", "Змінити ліміт показу", "<— Назад"]
    evn_push = user_db.need_evening_push
    on_or_off_push_word = 'Виключити' if evn_push else "Включити"
    profile_buttons[1] = profile_buttons[1].format(on_or_off_push_word)

    profile_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    cards_but = KeyboardButton(profile_buttons[0])
    change_push_but = KeyboardButton(profile_buttons[1])
    change_limit_but = KeyboardButton(profile_buttons[2])
    back_but = KeyboardButton(profile_buttons[-1])
    profile_markup.add(cards_but, change_push_but)
    profile_markup.add(change_limit_but)
    profile_markup.add(back_but)
    return profile_markup, profile_buttons


def form_cards_markup(chat_id, proceed):
    from data import retrieve_all_cards_of_user
    cards_info = retrieve_all_cards_of_user(chat_id)
    if not cards_info:
        from data import UserTools
        user = UserTools(chat_id=chat_id)
        card_data = user.mono.take_personal_info()
        user.create_cards_in_db(card_data['accounts'])
        cards_info = retrieve_all_cards_of_user(chat_id)
    cards_markup = InlineKeyboardMarkup(row_width=1)
    for card_info in cards_info:
        # add something if user already have it chosen
        card_preview, type, currency_code, id = card_info.card_preview, card_info.type, card_info.currencyCode, card_info._id
        checked = "✅" if card_info.is_active else ""
        button_text = f"{checked} {type.title()} {card_preview[-6:]} {currencies[currency_code]} {checked}"
        button = InlineKeyboardButton(text=button_text, callback_data=f"card;change;{id}")
        cards_markup.add(button)
    if is_at_least_one_card_chosen(cards_info):
        callback_message = "card;done;"
        if proceed:
            callback_message += 'proceed'
        final_button = InlineKeyboardButton(text="Далі —>", callback_data=callback_message)
        cards_markup.add(final_button)
    return cards_markup


def collect_profile_description(user_db):
    limit = user_db.limit_value_to_show
    do_push = user_db.need_evening_push
    # monobank_token = user_db.monobank_token

    profile_description = f"Вечірня розсилка: {'✅' if do_push else '❌'}" \
                          f"\nЛіміт показу: {limit if limit >= 0 else '❌'} грн"
    return profile_description
