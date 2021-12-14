import mongoengine as me
from typing import List
from additional_tools import *
from mono import MonobankApi

config = take_creds()
connection_str = config['Mongo']['host']


class Data:
    """ Manage MongoDB connection """
    def __init__(self):
        self.connect()

    def connect(self):
        me.connect(host=connection_str, alias='default')
        print("connection success ")

    def disconnect(self):
        me.disconnect(alias='default')

    def __delete__(self, instance):
        self.disconnect()


class UserTools:
    """ Manage all stuff, related to User, including db """
    def __init__(self, **kwargs):
        if kwargs['user']:
            self.user_db = kwargs['user']
        else:
            self.user_db = _handle_user(**kwargs)  # return User table object
        self.is_profile_filled = True if self.user_db.monobank_token else False
        self.mono = MonobankApi(self.user_db.monobank_token) if self.is_profile_filled else False

    def update_mono_token(self, token):
        self.user_db.monobank_token = token
        self.user_db.save()

    def update_user_send_time(self):
        self.user_db.last_send_at = take_now()
        self.user_db.save()

    def set_profile_filled(self):
        self.is_profile_filled = True
        self.mono = MonobankApi(self.user_db.monobank_token)


# TABLE(S) _________________________________________
class User(me.Document):
    name = me.StringField(required=True)
    nickname = me.StringField()
    chat_id = me.IntField(required=True, unique=True)
    registered_at = me.DateTimeField(required=True)
    monobank_token = me.StringField()
    last_send_at = me.DateTimeField()
# ___________________________________________________


def retrieve_all_users_from_db() -> List[User]:
    users = User.objects
    users = [user for user in users if user.monobank_token]
    return users


def _handle_user(**kwargs) -> User:
    """ Find or create user """
    user = User.objects.filter(chat_id=kwargs['chat_id'])
    kwargs = dict(kwargs)
    if not len(user):
        registered_at = take_now()
        user = User(**kwargs, registered_at=registered_at)
        print(user.name)
        user.save()
    else:
        user = user[0]
    return user


if __name__ == '__main__':
    Data()
    retrieve_all_users_from_db()
