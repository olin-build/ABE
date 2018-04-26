#!/usr/bin/env python3
"""Document models for mongoengine"""
import random

from mongoengine import *
from bson import ObjectId


class Subscription(Document):
    """
    Model for subscriptions
    Should be kept in sync with the resource model, which generates swagger documentation.

    """
    sid = StringField(required=True, unique=True)
    labels = ListField(StringField())

    def __init__(self, **data):
        super(Subscription, self).__init__(**data)

    @staticmethod
    def new():
        return Subscription(sid='{:030x}'.format(random.randrange(16 ** 30)))

    @staticmethod
    def get_sample():
        subscription = Subscription.new()
        subscription.labels = 'hello featured carpe'.split()
        subscription.sid = 'deadbeef' + subscription.sid[8:]
        return subscription
