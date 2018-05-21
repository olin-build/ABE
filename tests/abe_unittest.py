import unittest

from pymongo import MongoClient

from . import MONGODB_TEST_DB_NAME, db


class TestCase(unittest.TestCase):
    """The abstract base class for ABE test cases.

    Use this class instead of `unittest.TestCase` for tests that use the
    database. It tears down the database after each test.

    Attributes:
        db: The MongoDB database for the test environment
    """

    def setUp(self):
        super().setUp()
        assert db.mongo_db_name == MONGODB_TEST_DB_NAME, \
            f"{__name__} must be imported before abe.database"

    def tearDown(self):
        super().tearDown()
        client = MongoClient()
        client.drop_database(MONGODB_TEST_DB_NAME)
        client.close()
