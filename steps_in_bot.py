from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from mono import *
from data import UserTools, retrieve_all_cards_of_user
from bot_stat_finance import TeleBot
from additional_tools import mono_inl_markup


class ProfilePoll:
    """ Filling profile of user """

    def __init__(self, bot: TeleBot, user: UserTools):
        self.user = user
        self.bot = bot
        self.chat_id = user.user_db.chat_id
        self.fill_profile()

    def fill_profile(self):
        self.bot.send_sticker(self.chat_id, data='CAACAgIAAxkBAAEDzAZh-5nUeO5cHSA4NS1B8OMvUMMVvgACfgADwZxgDAsUf929Iv3zIwQ')
        msg1 = """Можливість дивитись статистику твоїх витрат за останній місяць з’являється завдяки токену від <b>Monobank</b>.

З цим токеном я <b>НЕ зможу маніпулювати</b> коштами, а <b>лише спостерігати</b> за ними та інформувати тебе.
<i>Інформація про ваші витрати не зберігається нами, а постійно стягується у Монобанку.</i>"""
        self.bot.send_message(self.chat_id, text=msg1, reply_markup=ReplyKeyboardRemove(selective=False), parse_mode='html')

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


def collect_statistic(keyboard_item, cid, mono):
    mess_to_send = ''
    res = []
    user = UserTools(chat_id=cid)
    limit = user.user_db.limit_value_to_show
    cards_acids = retrieve_all_cards_of_user(cid, active=True)
    for card in cards_acids:
        res_one = mono.statistic_for_period(unit=keyboard_item['unit'], sign='+-', account_id=card._id, limit=limit)
        res_one['type'] = card.type
        res.append(res_one)
        mess_to_send += f'\n\n<b>{card.type.title()} card ({card.card_preview[-6:]}): {int(res_one["general"])} грн</b>' \
                        + answer_pattern.format(negative_spends=round(res_one['negative'], 2),
                                                positive=round(res_one['positive'], 2))
    if not cards_acids:
        mess_to_send = '\n\n<b>Тепер ти можеш визначати з яких карток слідкувати за витратами.</b>\n' \
                       '<i>(Профіль —> Управління картками)</i>'
        res.append(mono.statistic_for_period(unit=keyboard_item['unit'], sign='+-', account_id='0', limit=limit))
    res_df = pd.DataFrame(res)
    print(res_df)

    general_mess = "{smile} {general_spends} {time_unit}".format(smile=keyboard_item['smile'],
                                                                 general_spends=int(res_df['general'].sum()),
                                                                 time_unit=keyboard_item['ukr_str']) \
                   + answer_pattern.format(negative_spends=round(res_df['negative'].sum(), 2),
                                           positive=round(res_df['positive'].sum(), 2))
    mess_to_send = general_mess + mess_to_send
    return mess_to_send
