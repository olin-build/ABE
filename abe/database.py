#!/usr/bin/env python3
"""Connect to mongodb"""
import logging
import os

from mongoengine import connect

# These imports are for effect. They define the document types, that mongodb
# uses to unserialize.
from .document_models.event_documents import Event, RecurringEventExc  # noqa: F401
from .document_models.ics_documents import ICS  # noqa: F401
from .document_models.label_documents import Label  # noqa: F401
from .document_models.subscription_documents import Subscription  # noqa: F401

config_present = False
try:
    from .mongo_config import uri, use_local, db_name
except ImportError:
    use_local = False
    uri = None
    db_name = "no-config"
else:
    config_present = True

env_present = os.environ.get('MONGO_URI')

mongo_uri = os.getenv('MONGO_URI', uri) if not use_local else None
mongo_db_name = os.getenv('DB_NAME', os.getenv('HEROKU_APP_NAME', db_name))

connect(mongo_db_name, host=mongo_uri)

if env_present:
    location = 'uri from environment variable'
elif config_present and not use_local:
    location = 'uri from config file'
else:
    location = 'localhost'

logging.info('Using db "{}" with {}'.format(mongo_db_name, location))


def return_uri():
    return mongo_uri
