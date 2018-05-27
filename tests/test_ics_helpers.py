from datetime import datetime

import icalendar
from isodate import parse_datetime

from . import abe_unittest, db

# This import must occur after `from . import` sets the environment variables
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
        assert key in key
        event = testEvents[key]
        return db.Event(**event)

    def test_create_ics_event(self):
        with self.subTest('basic event'):
            event = self.get_test_event('basic')
            ics_event = ics_helpers.create_ics_event(event)
            self.assertEqual(ics_event.get('uid'), icalendar.vText('5ace6ff26a6942408317afd3'))  # or UID ?
            self.assertEqual(ics_event.get('summary'), icalendar.vText("Test event"))
            self.assertEqual(ics_event.get('description'), icalendar.vText("Event description"))
            self.assertEqual(ics_event.get('location'), icalendar.vText("Room of Requirement"))
            self.assertEqual(ics_event.get('dtstart').dt, parse_datetime('2017-06-01T15:00:00Z'))
            self.assertEqual(ics_event.get('dtend').dt, parse_datetime('2017-06-01T15:30:00Z'))
            self.assertEqual(ics_event.get('RECURRENCE-ID'), None)
            self.assertEqual(ics_event.get('rrule'), None)

        with self.subTest('all-day event'):
            event = self.get_test_event('all_day')
            ics_event = ics_helpers.create_ics_event(event)
            self.assertEqual(ics_event.get('dtstart'), None)
            self.assertEqual(ics_event.get('dtend'), None)
            self.assertEqual(ics_event.get('dtstart;VALUE=DATE'), icalendar.vText(b'20170601'))
            self.assertEqual(ics_event.get('dtend;VALUE=DATE'), None)

        # TODO: multi-day event should have dtend;VALUE=DATE

        # TODO: test recurring events
        # TODO: test that id is from event['sid']
        # TODO: test RECURRENCE_ID from event['rec_id']
        # TODO: test byday, bymonthday, byyearday in RRULE

        with self.subTest('locationless events'):
            # There was previously a bug where this returned a location of "none"
            event = self.get_test_event('no_location')
            ics_event = ics_helpers.create_ics_event(event)
            self.assertEqual('location' in ics_event, False)
