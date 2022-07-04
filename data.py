from json import dumps

import mongoengine as me
from redis import Redis
from typing import List
from additional_tools import take_creds, take_now
from mono import MonobankApi

config = take_creds()


class Data:
    """ Manage MongoDB connection """

    def __init__(self):
        self.redis = None
        self.mongo = None
        self._connect_mongo()
        self._connect_redis()

    def _connect_mongo(self):
        mongo_connection_str = config['Mongo']['host']
        self.mongo = me.connect(host=mongo_connection_str, alias='default')
        print("connection success ")

    def _connect_redis(self):
        redis_connection_str = config['Redis']['host']
        redis_password = config['Redis']['password']
        self.redis = Redis(host=redis_connection_str, port=12930,
                           password=redis_password, decode_responses=True)

    def get_redis_connection(self):
        return self.redis

    def get_mongo_connection(self):
        return self.mongo

    def get_from_redis(self, key):
        try:
            return self.redis.get(key)
        except:
            self._connect_redis()
            return self.redis.get(key)

    def put_in_redis(self, key, value):
        try:
            self.redis.set(key, dumps(value))
        except:
            self._connect_redis()
            self.redis.set(key, dumps(value))

    def disconnect(self):
        me.disconnect(alias='default')
        self.redis.close()

    def __delete__(self, instance):
        self.disconnect()


data_object = Data()


class UserTools:
    """ Manage all stuff, related to User, including db """

    def __init__(self, **kwargs):
        if kwargs.get('user', None):
            self.user_db = kwargs['user']  # TO_IMPROVE (is it valid)
        else:  # add if only chat_id exist (or name, nickname)
            self.user_db = self._handle_user(**kwargs)  # return User table object
        self.is_profile_filled = True if self.user_db.monobank_token else False
        self.mono = MonobankApi(self.user_db.monobank_token) if self.is_profile_filled else False

    def _handle_user(self, **kwargs):
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

    def update_mono_token(self, token):
        self.user_db.monobank_token = token
        self.user_db.save()

    def update_user_send_time(self):
        self.user_db.last_send_at = take_now()
        self.user_db.save()

    def change_need_evening_push(self, value=''):
        if value == '':
            last_nep = self.user_db.need_evening_push
            value = False if last_nep else True
        self.user_db.need_evening_push = value
        self.user_db.save()

    def change_limit_of_value(self, value):
        user = User.objects.filter(chat_id=self.user_db.chat_id)[0]
        user.limit_value_to_show = int(value)
        user.save()

    def set_profile_filled(self):
        self.is_profile_filled = True
        self.mono = MonobankApi(self.user_db.monobank_token)

    def create_cards_in_db(self, cards_dict):
        right_columns = ['type', 'currencyCode']
        # card_right_dict = [{k: v for k, v in card.items() if k in right_columns} for card in cards_dict]
        for card in cards_dict:
            right_card = {'_id': card['id'], 'type': card['type'], 'currencyCode': card['currencyCode'],
                          'is_active': False, 'user': self.user_db, 'card_preview': card['maskedPan'][0]}
            card_item = Cards(**right_card)
            card_item.save()

    def is_minute_since_activity_passed(self):
        return (take_now() - self.user_db.last_send_at).total_seconds() > 59


# TABLE(S) _________________________________________
class User(me.Document):
    name = me.StringField(required=True)
    nickname = me.StringField()
    chat_id = me.IntField(required=True, unique=True)
    registered_at = me.DateTimeField(required=True)
    monobank_token = me.StringField()
    last_send_at = me.DateTimeField()
    need_evening_push = me.BooleanField(default=True)
    limit_value_to_show = me.IntField(default=0, min_value=0)


class Cards(me.Document):
    _id = me.StringField(required=True)
    card_preview = me.StringField(required=True)
    type = me.StringField()
    currencyCode = me.IntField(required=True)  # ISO 4217
    user = me.ReferenceField(required=True, document_type=User)
    is_active = me.BooleanField(default=True, required=True)


class Category(me.Document):
    mcc = me.IntField(required=True)
    shortDescription = me.StringField()
    fullDescription = me.StringField()
    type = me.StringField()
    description = me.StringField(required=True)
    meta = {
        'indexes': ['mcc']
    }

# ___________________________________________________


#  ___________________________________________________


def change_activity_of_card(id):
    card_obj = Cards.objects.filter(_id=id)[0]
    new_activity = False if card_obj.is_active else True
    card_obj.is_active = new_activity
    card_obj.save()


def retrieve_all_cards_of_user(chat_id, active=False):
    user = User.objects.filter(chat_id=chat_id)
    if active:
        cards = Cards.objects.filter(user=user[0], is_active=True)
    else:
        cards = Cards.objects.filter(user=user[0])
    return cards


def retrieve_all_users_from_db() -> List[User]:
    users = User.objects
    users = [user for user in users if user.monobank_token]
    return users


if __name__ == '__main__':
    Data()
    retrieve_all_users_from_db()
