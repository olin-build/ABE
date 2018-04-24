import os
import unittest
from datetime import datetime

from pymongo import MongoClient


testDbName = "abe-unittest"

# TODO: add test cases for YEARLY frequency (are there others)?
# TODO: add test cases for by_month, by_month_day
# TODO: add test cases for count, interval
recurringEvents = dict(
    weekly={
        "visibility": "olin",
        'title': 'Weekly Test Event',
        'location': 'Quiet Reading Room',
        'description': '',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        'recurrence_end': datetime(2017, 7, 31),
        "labels": [],
        'recurrence': {
            'frequency': 'WEEKLY',
            'count': '10',
            'interval': '1',
            'until': datetime(2017, 7, 31),
            'by_day': ["MO", "TU", "WE", "TH", "FR"]
        }
    },
)


class RecurrenceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["DB_NAME"] = testDbName
        os.environ["MONGO_URI"] = ""
        # These imports need to happen after setting the environment variable
        # TODO: factor these from the tests to a test helper
        from abe import database as db
        self.db = db

    def tearDown(self):
        client = MongoClient()
        client.drop_database(testDbName)
        client.close()

    def get_test_event(self, key):
        db = self.db
        assert key in key
        event = recurringEvents[key]
        return db.Event(**event)

    def test_instance_creation(self):
        # This import has to happen after setUp sets the environment variables
        from abe.helper_functions import sub_event_helpers
        event = self.get_test_event('weekly')

        with self.subTest("no start or end date"):
            instances = sub_event_helpers.instance_creation(event)
            # With neither of the optional params specified, it should enumerate all instances of the recurring event
            self.assertEqual(len(instances), 10)

        with self.subTest("start and date outside recurrence"):
            instances = sub_event_helpers.instance_creation(
                event,
                start=datetime(2017, 1, 1),
                end=datetime(2018, 1, 1))
            # Should return every instance of the recurring event.
            self.assertEqual(len(instances), 10)

        with self.subTest("start and date inside recurrence"):
            instances = sub_event_helpers.instance_creation(
                event,
                start=datetime(2017, 7, 20),
                end=datetime(2027, 7, 31))
            # Should return all instances of the recurring event that happen within the query range
            self.assertEqual(len(instances), 8)