from random import randint
from time import sleep
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telebot import TeleBot

from bot_stat_finance import main_markup
from mono import *
from data import update_mono_token


def fill_profile(bot, cid):
    msg2 = 'Введи свій Монобанк токен (за посиланням): https://api.monobank.ua/'
    bot.send_message(cid, msg2)
    bot.register_next_step_handler_by_chat_id(chat_id=cid,
                                              callback=acquire_token,
                                              bot=bot)


def acquire_token(message, **kwargs):
    bot = kwargs['bot']
    cid = message.chat.id
    taken_token = message.text

    test_data = take_payments(token=taken_token)
    if isinstance(test_data, dict):
        print(test_data.get('errorDescription', None))
        msg_err = 'Токен не правильний. Спробуй ще раз.'
        bot.send_message(cid, msg_err)
        fill_profile(bot, cid)
    else:
        msg_success = 'Юуху, токен правильний. Насолоджуйся)'
        update_mono_token(cid, taken_token)
        bot.send_message(cid, msg_success, reply_markup=main_markup)
