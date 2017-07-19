#!/usr/bin/env python3
"""Document models for mongoengine"""
from mongoengine import *
from bson import ObjectId

class ICS(Document):
	"""Model for links to ics feeds"""
	url = StringField()