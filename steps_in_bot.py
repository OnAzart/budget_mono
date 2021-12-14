from mono import *


class ProfilePoll:
    """ Filling profile of user """
    def __init__(self, bot, user):
        self.user = user
        self.bot = bot
        self.chat_id = user.user_db.chat_id
        self.fill_profile()

    def fill_profile(self):
        msg2 = 'Введи свій Монобанк токен (за посиланням): https://api.monobank.ua/'
        self.bot.send_message(self.chat_id, msg2)
        self.bot.register_next_step_handler_by_chat_id(chat_id=self.chat_id,
                                                       callback=self._acquire_token,
                                                       bot=self.bot)

    def _acquire_token(self, message, **kwargs):
        taken_token = message.text
        test_data = take_payments(token=taken_token)
        if isinstance(test_data, dict):
            print(test_data.get('errorDescription', None))
            msg_err = 'Токен не правильний. Спробуй ще раз.'
            self.bot.send_message(self.chat_id, msg_err)
            self.fill_profile()
        else:
            msg_success = 'Юуху, токен правильний. Насолоджуйся)'
            self.user.update_mono_token(self.chat_id, taken_token)
            self.bot.send_message(self.chat_id, msg_success, reply_markup=main_markup)
            self.user.set_profile_filled()

