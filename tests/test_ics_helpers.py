from datetime import datetime
from unittest import skip

import icalendar

from . import abe_unittest
from .context import abe  # noqa: F401

# This import has to happen after .context sets the environment variables
from abe.helper_functions import ics_helpers  # isort:skip

testEvents = dict(
    basic={
        'id': '5ace6ff26a6942408317afd3',
        'visibility': 'olin',
        'title': 'Test event',
        'location': 'Room of Requirement',
        'description': 'Event description',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        'labels': [],
    },
    all_day={
        'id': '5ace6ff26a6942408317afd3',
        'visibility': 'olin',
        'title': 'Test event',
        'location': 'Room of Requirement',
        'description': 'Event description',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        'recurrence_end': datetime(2017, 7, 31),
        'allDay': True,
        'labels': [],
    },
    recurrence={
        'sid': '5ace6ff26a6942408317afd3',
        'visibility': 'olin',
        'title': 'Test event',
        'location': 'Room of Requirement',
        'description': 'Event description',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        'recurrence_end': datetime(2017, 7, 31),
        'labels': [],
        'recurrence': {
            'frequency': 'WEEKLY',
            'count': '10',
            'interval': '1',
            'until': datetime(2017, 7, 31),
            'by_day': ['MO', 'TU', 'WE', 'TH', 'FR'],
        },
    },
    no_location={
        'id': '5ace6ff26a6942408317afd3',
        'visibility': 'olin',
        'title': 'Test event',
        'description': 'Event description',
        'start': datetime(2017, 6, 1, 15, 0),
        'end': datetime(2017, 6, 1, 15, 30),
        'recurrence_end': datetime(2017, 7, 31),
        'labels': [],
        'recurrence': {
            'frequency': 'WEEKLY',
            'count': '10',
            'interval': '1',
            'until': datetime(2017, 7, 31),
            'by_day': ['MO', 'TU', 'WE', 'TH', 'FR'],
        },
    }
)


class IcsHelpersTestCase(abe_unittest.TestCase):

    # TODO: DRY w/ method in RecurrenceTestCase
    def get_test_event(self, key):
        db = self.db
        assert key in key
        event = testEvents[key]
        return db.Event(**event)

    def test_create_ics_event(self):
        with self.subTest('basic event'):
            event = self.get_test_event('basic')
            ics_event = ics_helpers.create_ics_event(event)
            self.assertEqual(ics_event.get('uid'), icalendar.vText("5ace6ff26a6942408317afd3"))  # or UID ?
            self.assertEqual(ics_event.get('summary'), icalendar.vText("Test event"))
            self.assertEqual(ics_event.get('description'), icalendar.vText("Event description"))
            self.assertEqual(ics_event.get('location'), icalendar.vText("Room of Requirement"))
            # TODO: test dtstart and dtend
            # self.assertEqual(ics_event.get('dtstart'), …)
            # self.assertEqual(ics_event.get('dtend'), …)
            self.assertEqual(ics_event.get('RECURRENCE-ID'), None)
            self.assertEqual(ics_event.get('rrule'), None)

        with self.subTest('all-day event'):
            event = self.get_test_event('all_day')
            ics_event = ics_helpers.create_ics_event(event)
            # TODO: test the date
            self.assertEqual(ics_event.get('dtstart'), None)
            self.assertEqual(ics_event.get('dtend'), None)

        with self.subTest('recurring events'):
            self.skipTest('unimplemented test')
            # TODO: test that id is from event['sid']
            # TODO: test RECURRENCE_ID from event['rec_id']
            # TODO: test byday, bymonthday, byyearday in RRULE
        with self.subTest('locationless events'):
            event = self.get_test_event('no_location')
            ics_event = ics_helpers.create_ics_event(event)
            self.assertEqual(ics_event.has_key('location'), False)
            

    @skip('Unimplemented test')
    def test_create_ics_recurrence(self):
        pass
        # TODO: ics_helpers.create_ics_recurrence(new_event, recurrence)

    @skip('Unimplemented test')
    def test_mongo_to_ics(self):
        pass
        # TODO: ics_helpers.mongo_to_ics(events)

    @skip('Unimplemented test')
    def test_ics_to_dict(self):
        pass
        # TODO: ics_helpers.ics_to_dict(component, labels, ics_id=None)

    @skip('Unimplemented test')
    def test_extract_ics(self):
        pass
        # TODO: ics_helpers.extract_ics(cal, ics_url, labels=None)

    @skip('Unimplemented test')
    def test_update_ics_to_mongo(self):
        pass
        # TODO: ics_helpers.update_ics_to_mongo(component, labels)

    @skip('Unimplemented test')
    def test_update_ics_feed(self):
        pass
        # TODO: ics_helpers.update_ics_feed()
