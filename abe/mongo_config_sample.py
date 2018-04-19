#!/usr/bin/env python
"""Configuration for MongoDB connection

app.py first checks if mongo_config.py exists, then connects with the default
localhost setup if `use_local` is True. If `use_local` is False, it connects to
MongoDB with the `mongo_uri` string.

https://docs.mongodb.com/manual/reference/connection-string/
"""

db_name = 'testing'  # name of database to use, overridden by uri
use_local = True  # ignore the uri and use locally hosted mongodb instance

mongodb_options = {
    "username": "fred",
    "password": "fluffy stoic cactus",
    "host": "localhost",
    "port": "27017",  # default mongodb port
}
uri_format = 'mongodb://{username}:"{password}"@{host}:{port}'
uri = uri_format.format(**mongodb_options)
