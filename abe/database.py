#!/usr/bin/env python3
"""Connect to mongodb"""
import logging
import os
import re

from mongoengine import connect

# These imports are for effect. They define the document types, that mongodb
# uses to unserialize.
from .document_models.app_documents import App  # noqa: F401
from .document_models.event_documents import Event, RecurringEventExc  # noqa: F401
from .document_models.ics_documents import ICS  # noqa: F401
from .document_models.label_documents import Label  # noqa: F401
from .document_models.subscription_documents import Subscription  # noqa: F401


# Support legacy environment variable names
if os.environ.get('MONGO_URI') and not os.environ.get('MONGODB_URI'):
    os.environ['MONGODB_URI'] = os.environ['MONGO_URI']

mongo_uri = os.getenv('MONGODB_URI')
mongo_db_name = os.getenv('DB_NAME', os.getenv('HEROKU_APP_NAME', 'abe'))

connect(mongo_db_name, host=mongo_uri)


def sanitize_passwords(s):
    return re.sub(r':[^,/]+', ':•••', s) if s else s


logging.info('Using db %r on %s', mongo_db_name, sanitize_passwords(mongo_uri) or 'localhost')


def return_uri():
    return mongo_uri
