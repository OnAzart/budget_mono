import mongoengine as me
from additional_tools import *


config = take_creds()
connection_str = config['Mongo']['host']


class Data:
    def __init__(self):
        self.connect()

    def connect(self):
        me.connect(host=connection_str, alias='default')
        print("connection success ")

    def disconnect(self):
        me.disconnect(alias='default')

    def __delete__(self, instance):
        self.disconnect()


def handle_user(**kwargs):
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


def update_mono_token(cid, token):
    user = User.objects.filter(chat_id=cid)[0]
    user.monobank_token = token
    user.save()


def update_user_send_time(cid):
    user = User.objects.filter(chat_id=cid)[0]
    user.last_send_at = take_now()
    user.save()


def retrieve_users_from_db(): #########
    users = User.objects
    users = [user for user in users if user.monobank_token]
    return users


# TABLES
class User(me.Document):
    name = me.StringField(required=True)
    nickname = me.StringField()
    chat_id = me.IntField(required=True, unique=True)
    registered_at = me.DateTimeField(required=True)
    monobank_token = me.StringField()
    last_send_at = me.DateTimeField()


if __name__ == '__main__':
    Data()
    retrieve_users_from_db()
