import os
import unittest

from pymongo import MongoClient

MONGODB_TEST_DB_NAME = "abe-unittest"
os.environ["DB_NAME"] = MONGODB_TEST_DB_NAME
os.environ["MONGO_URI"] = ""

from abe import database as db  # isort:skip # noqa: E402


class TestCase(unittest.TestCase):
    """The abstract base class for ABE test cases.

    Use this class instead of `unittest.TestCase` for tests that use the
    database. It tears down the database after each test.

    Attributes:
        db: The MongoDB database for the test environment
    """

    def setUp(self):
        # This import needs to happen after setting the environment variables
        # above
        self.db = db
        assert db.mongo_db_name == MONGODB_TEST_DB_NAME, \
            f"{__name__} must be imported before abe.database"

    def tearDown(self):
        client = MongoClient()
        client.drop_database(MONGODB_TEST_DB_NAME)
        client.close()
