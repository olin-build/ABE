#!/usr/bin/env python3
"""Document models for mongoengine"""
from mongoengine import *
from bson import ObjectId


class Label(Document):
    """Model for labels of events"""
    name = StringField(required=True, unique=True)  # TODO: set to primary key?
    description = StringField()
    url = URLField()