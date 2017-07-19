#!/usr/bin/env python3
"""Miscellaneous helper functions of varying usefulness
helpful inspiration: https://gist.github.com/jason-w/4969476
"""
from mongoengine import ValidationError

import logging
import pdb
import pytz

from icalendar import Calendar, Event, vCalAddress, vText, vDatetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY, DAILY, YEARLY
from datetime import datetime, timedelta, timezone
from bson import objectid
from mongoengine import *
from icalendar import Calendar

import isodate
import dateutil.parser
import requests

from . import database as db


















