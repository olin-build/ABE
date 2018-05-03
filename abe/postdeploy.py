#!/usr/bin/env python3
"""Script used to create databases for Heroku review apps.

The postdeploy script in app.json invokes this.
"""
import logging
import os

from pymongo import MongoClient

from . import database as db
from .database import mongo_uri
from .sample_data import load_data

logging.basicConfig(level=logging.DEBUG)


logging.info('Performing postdeploy process')
db_name = os.getenv("HEROKU_APP_NAME", "testing")
logging.warning('Dropping mongodb db %s', db_name)
client = MongoClient(mongo_uri)  # use pymongo to drop database
client.drop_database(db_name)
client.close()
logging.warning('Filling mongodb db %s with sample data', db_name)
load_data(db)  # fill database with mongoengine
logging.info('Finished postdeploy process')
