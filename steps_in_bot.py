import pandas as pd
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton
from telebot import TeleBot

from additional_tools import mono_inl_markup, form_cards_markup, main_markup, take_start_of_dateunit, take_now, \
    answer_pattern
from data import UserTools, retrieve_all_cards_of_user, data_object
from mono import MonobankApi


class ProfilePoll:
    """ Filling profile of user """

    def __init__(self, bot: TeleBot, user: UserTools):
        self.user = user
        self.bot = bot
        self.chat_id = user.user_db.chat_id
        self.fill_profile()

    def fill_profile(self):
        self.bot.send_sticker(self.chat_id,
                              data='CAACAgIAAxkBAAEDzAZh-5nUeO5cHSA4NS1B8OMvUMMVvgACfgADwZxgDAsUf929Iv3zIwQ')
        msg1 = """Можливість дивитись статистику твоїх витрат за останній місяць з’являється завдяки токену від <b>Monobank</b>.

З цим токеном я <b>НЕ зможу маніпулювати</b> коштами, а <b>лише спостерігати</b> за ними та інформувати тебе.
<i>Інформація про ваші витрати не зберігається нами, а постійно стягується у Монобанку.</i>"""
        self.bot.send_message(self.chat_id, text=msg1, reply_markup=ReplyKeyboardRemove(selective=False),
                              parse_mode='html')

        msg2 = 'Дізнайся та активуй свій токен, натиснувши на кнопку, а потім відправ його мені в чат 👇'
        self.bot.send_message(self.chat_id, text=msg2, reply_markup=mono_inl_markup)
        self.bot.register_next_step_handler_by_chat_id(chat_id=self.chat_id,
                                                       callback=self._acquire_token)

    def _acquire_token(self, message):
        taken_token = message.text

        card_data = MonobankApi(token=taken_token).take_personal_info()
        if not card_data.get('accounts', None):
            print(card_data.get('errorDescription', None))
            msg_err = 'Токен не правильний. Спробуй ще раз.'
            self.bot.send_message(self.chat_id, msg_err)
            self.fill_profile()
        else:
            msg_success = 'Юуху, токен правильний. Насолоджуйся)'
            self.user.update_mono_token(taken_token)
            self.user.create_cards_in_db(card_data['accounts'])
            # self.bot.send_message(self.chat_id, msg_success, reply_markup=main_markup)
            choose_card(bot=self.bot, chat_id=self.chat_id)
            self.user.set_profile_filled()


def choose_card(bot, chat_id='', call='', proceed=True):
    chat_id = chat_id if not call else call.message.chat.id
    card_markup = form_cards_markup(chat_id, proceed)
    if call:
        msg_id = call.message.message_id
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=card_markup)
    else:
        bot.send_message(text='Витрати з яких карток ти хочеш відслідковувати?',
                         reply_markup=card_markup, chat_id=chat_id)


def do_need_an_evening_push(bot, cid):
    # ask message with markup
    msg_push = """Чи варто тобі надсилати статистику витрат щовечора?"""
    but_yes = InlineKeyboardButton(text='Так', callback_data='push;yes;')
    but_no = InlineKeyboardButton(text='Ні', callback_data='push;no;')
    markup_push = InlineKeyboardMarkup()
    markup_push.row(but_yes, but_no)
    # handle: run data function with result and call value limit
    bot.send_message(text=msg_push, reply_markup=markup_push, chat_id=cid)


def do_need_a_value_limit(bot, cid):
    # ask message with markup
    msg_limit = """Ти маєш можливість відключити врахування переказу більше певної суми. 
Введи суму в гривнях, більше якої не показувати (для прикладу 5000)."""
    markup_limit = ReplyKeyboardMarkup(resize_keyboard=True)
    markup_limit.add(KeyboardButton('Іншим разом 😊'))
    bot.send_message(text=msg_limit, reply_markup=markup_limit, chat_id=cid)
    bot.register_next_step_handler_by_chat_id(chat_id=cid, bot=bot, callback=handle_value_limit, cid=cid)
    # handle: if yes — run data function, if no — call finish stage


def handle_value_limit(message, bot, cid):
    value = message.text
    if value == 'Іншим разом 😊' or not isinstance(value, str):
        pass
    elif value.isdigit():
        user = UserTools(chat_id=cid)
        user.change_limit_of_value(value)
    finish_stage(chat_id=cid, bot=bot)


def finish_stage(bot, chat_id):
    # chat_id = call.message.chat.id
    msg = "Клас, тепер я розумію що тобі потрібно 😊" \
          "\n\nДізнавайся статистику витрат і слідкуй за ними." \
          "\n& Go long 💸 "
    bot.send_message(chat_id=chat_id, text=msg, reply_markup=main_markup)


def collect_statistic(keyboard_item, cid='', mono='', from_tmsp='', to_tsmp=''):
    if not mono:
        mono = UserTools(cid=cid).mono
    if not all([from_tmsp, to_tsmp]):
        from_tsmp = take_start_of_dateunit(unit=keyboard_item['unit'])
        to_tsmp = str(int(take_now().timestamp()))
    mess_to_send = ''
    aggregated_results = []
    payments = []
    user = UserTools(chat_id=cid)
    limit = user.user_db.limit_value_to_show

    cards_of_user = retrieve_all_cards_of_user(cid, active=True)
    for card in cards_of_user:
        aggregated_res_one, payments_one = mono.statistic_for_period(unit=keyboard_item['unit'], sign='+-',
                                                                     account_id=card._id, limit=limit,
                                                                     from_=from_tsmp, to_=to_tsmp)
        aggregated_res_one['type'] = card.type
        aggregated_results.append(aggregated_res_one)
        payments.extend(payments_one)
        mess_to_send += f'\n\n<b>{card.type.title()} card ({card.card_preview[-6:]}): {int(aggregated_res_one["general"])} грн</b>' \
                        + answer_pattern.format(negative_spends=round(aggregated_res_one['negative'], 2),
                                                positive=round(aggregated_res_one['positive'], 2))
    if not cards_of_user:
        mess_to_send = '\n\n<b>Тепер ти можеш визначати з яких карток слідкувати за витратами.</b>\n' \
                       '<i>(Профіль —> Управління картками)</i>'
        aggregated_res_one, payments_one = mono.statistic_for_period(unit=keyboard_item['unit'], sign='+-',
                                                                     account_id='0', limit=limit)
        payments.extend(payments_one)
        aggregated_results.append(aggregated_res_one)
    aggregated_results_df = pd.DataFrame(aggregated_results)
    print(aggregated_results_df)

    general_mess = "{smile} {general_spends} {time_unit}".format(smile=keyboard_item['smile'],
                                                                 general_spends=int(
                                                                     aggregated_results_df['general'].sum()),
                                                                 time_unit=keyboard_item['ukr_str']) \
                   + answer_pattern.format(negative_spends=round(aggregated_results_df['negative'].sum(), 2),
                                           positive=round(aggregated_results_df['positive'].sum(), 2))
    mess_to_send = general_mess + mess_to_send
    key = f'{cid}-{from_tsmp}-{to_tsmp}'
    data_object.put_in_redis(key, payments)
    callback_for_details = f'details;;{key};{keyboard_item["unit"]}'
    return mess_to_send, callback_for_details


if __name__ == '__main__':
    from json import loads
    from data import data_object
    from plot.plots import Plot
    pays = loads(data_object.get_from_redis('{cid}-{from_tsmp}-{to_tsmp}'))
    Plot(pays, area_plot='today')
