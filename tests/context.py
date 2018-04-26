#!/usr/bin/env python3
"""Provide context for imports of ABE.
Referenced from The Hitchhiker's Guide to Python.
http://docs.python-guide.org/en/latest/writing/structure/#test-suite
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MONGODB_TEST_DB_NAME = "abe-unittest"
os.environ["DB_NAME"] = MONGODB_TEST_DB_NAME
os.environ["MONGO_URI"] = ""

# These imports have to go after the environment variables are set
import abe  # isort:skip # noqa: E402 F401
from abe import database as db  # isort:skip # noqa: E402
