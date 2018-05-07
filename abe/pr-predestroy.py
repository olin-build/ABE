#!/usr/bin/env python3
"""Script used to drop databases for Heroku review apps after closing.

The pre-predestroy script in app.json invokes this.
"""
import logging
import os

from pymongo import MongoClient

from .database import mongo_uri

logging.basicConfig(level=logging.DEBUG)

logging.info('Performing predestroy process')
# TODO: default to 'testing', like the postdeploy.py?
db_name = os.getenv('HEROKU_APP_NAME', None)
if db_name:
    logging.warning('Dropping mongodb db %s', db_name)
    client = MongoClient(mongo_uri)  # use pymongo to drop database
    client.drop_database(db_name)
    client.close()
else:
    logging.error('No env variable found with name "HEROKU_APP_NAME"')
    # TODO: should this exit with an error?
logging.info('Finished predestroy process')
