#!/usr/bin/env python3
"""Document models for mongoengine"""
import random

from mongoengine import *
from bson import ObjectId


class Subscription(Document):
    """
    Model for subscriptions

    """
    id = StringField(required=True, unique=True, primary_key=True)
    labels = ListField(StringField())

    def __init__(self):
        super(Subscription, self).__init__()
        self.id = '{:030x}'.format(random.randrange(16 ** 30))

    @staticmethod
    def get_sample():
        subscription = Subscription()
        subscription.labels = 'hello featured carpe'.split()
        subscription.id = 'deadbeef'+subscription.id[8:]
        return subscription
