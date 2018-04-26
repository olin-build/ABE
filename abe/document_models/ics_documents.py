#!/usr/bin/env python3
"""Document models for mongoengine"""
from mongoengine import *
from bson import ObjectId


class ICS(Document):
    """
    Model for links to ics feeds
    These links are accessed by the celery worker to refresh the calendar from the ics feeds
    Should be kept in sync with the resource model, which generates swagger documentation.

    Fields:
    url 			Stores the link to an ics feed. Required
                                Takes a stringfield

    labels 			Labels associated with all events from this feed. Required
                                Takes a list of strings with choice from the labels database

    """
    url = StringField()
    labels = ListField(StringField())
