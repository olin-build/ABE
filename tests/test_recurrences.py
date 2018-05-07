from datetime import datetime

from abe.helper_functions import recurring_helpers

from . import abe_unittest
from .context import abe  # noqa: F401

# This import has to happen after .context sets the environment variables
from abe.helper_functions import sub_event_helpers  # isort:skip

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
            'interval': '1',
            'until': datetime(2017, 7, 31),
            'by_day': ["MO", "TU", "WE", "TH", "FR"]
        }
    },
    count={
        "visibility": "olin",
        'title': '10 Count Recurring Event',
        'location': 'Quiet Reading Room',
        'description': '',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        "labels": [],
        'recurrence': {
            'frequency': 'WEEKLY',
            'count': '10',
            'interval': '1',
            'by_day': ["MO", "TU", "WE", "TH", "FR"]
        }
    },
    forever={
        "visibility": "olin",
        'title': 'Forever Recurring Event',
        'location': 'Quiet Reading Room',
        'description': '',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        "labels": [],
        'recurrence': {
            'frequency': 'WEEKLY',
            'interval': '1',
            'by_day': ["MO", "TU", "WE", "TH", "FR"]
        }
    },
)


class RecurrenceTestCase(abe_unittest.TestCase):

    # TODO: DRY w/ method in IcsHelpersTestCase
    def get_test_event(self, key):
        db = self.db
        assert key in key
        event = recurringEvents[key]
        return db.Event(**event)

    def test_instance_creation(self):
        event = self.get_test_event('weekly')
        event_count = self.get_test_event('count')
        event_forever = self.get_test_event('forever')

        with self.subTest("no start or end date"):
            instances = sub_event_helpers.instance_creation(event)
            # With neither of the optional params specified, it should enumerate all instances of the recurring event
            self.assertEqual(len(instances), 42)

        with self.subTest("start and date outside recurrence"):
            instances = sub_event_helpers.instance_creation(
                event,
                start=datetime(2017, 1, 1),
                end=datetime(2018, 1, 1))
            # Should return every instance of the recurring event.
            self.assertEqual(len(instances), 42)

        with self.subTest("start and date inside recurrence"):
            instances = sub_event_helpers.instance_creation(
                event,
                start=datetime(2017, 7, 20),
                end=datetime(2027, 7, 31))
            # Should return all instances of the recurring event that happen within the query range
            self.assertEqual(len(instances), 42)

        with self.subTest("Wide search range with count event"):
            instances = sub_event_helpers.instance_creation(
                event_count,
                start=datetime(2017, 6, 1),
                end=datetime(2017, 7, 31))
            # Should return only ten events since count should override rUntil
            self.assertEqual(len(instances), 10)

        with self.subTest("Start date partway through count recurrence"):
            # Uses recurring_to_full because it is the method that actually selects the events in range
            instances = recurring_helpers.recurring_to_full(
                event_count,
                [],
                datetime(2017, 6, 4),
                datetime(2017, 7, 31))
            # Should return only the events that occur after the start date
            self.assertEqual(len(instances), 8)

        with self.subTest("Forever recurrent event with start query after event start"):
            instances = recurring_helpers.recurring_to_full(
                event_forever,
                [],
                datetime(2018, 1, 1),
                datetime(2018, 1, 31))
            self.assertEqual(len(instances), 22)

        with self.subTest("Forever recurrent event with start query before event start"):
            instances = recurring_helpers.recurring_to_full(
                event_forever,
                [],
                datetime(2017, 5, 1),
                datetime(2017, 7, 31))
            self.assertEqual(len(instances), 42)
