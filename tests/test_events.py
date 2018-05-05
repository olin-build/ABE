from unittest import skip

import flask
import isodate

from . import abe_unittest
from .context import abe  # noqa: F401

# These imports have to happen after .context sets the environment variables
import abe.app  # isort:skip
from abe import sample_data  # isort:skip


class EventsTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.app = abe.app.app.test_client()
        sample_data.load_data(self.db)

    def test_get_events(self):
        with self.subTest("a six-month query returns some events"):
            response = self.app.get('/events/?start=2017-01-01&end=2017-07-01')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(flask.json.loads(response.data)), 25)

        with self.subTest("a one-year query returns all events"):
            response = self.app.get('/events/?start=2017-01-01&end=2018-01-01')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(flask.json.loads(response.data)), 69)

        with self.subTest("a two-year query is too long"):
            response = self.app.get('/events/?start=2017-01-01&end=2019-01-01')
            self.assertEqual(response.status_code, 404)

        with self.subTest("a one-year query works for leap years"):
            response = self.app.get('/events/?start=2020-01-01&end=2021-01-01')
            self.assertEqual(response.status_code, 200)

        with self.subTest("an unauthenticated sender retrieves only public events"):
            event_response = self.app.get('/events/?start=2017-01-01&end=2017-07-01')
            # TODO: change the following when #75 is implemented
            self.assertEqual(len(flask.json.loads(event_response.data)), 25)

    def test_post(self):
        event = {
            'title': 'test_post',
            'start': isodate.parse_datetime('2018-05-04T09:00:00')
        }

        with self.subTest("succeeds when required fields are present"):
            response = self.app.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

        with self.subTest("fails when fields are missing"):
            evt = event.copy()
            del evt['title']
            response = self.app.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'title'")

            evt = event.copy()
            del evt['start']
            response = self.app.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'start'")

        with self.subTest("fails when the client is not authorized"):
            response = self.app.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)

    # @skip("Unimplemented test")
    def test_put(self):
        # TODO: test success
        event = {
            'title': 'test_put',
            'start': isodate.parse_datetime('2018-05-04T09:00:00')
        }

        with self.subTest("succeeds when required fields are present"):
            response = self.app.put(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

        # TODO: test invalid id
        with self.subTest("fails when the event id is invalid"):
            response = self.app.put(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'title'")

        # TODO: test invalid data
        with self.subTest("fails when fields are missing"):
            evt = event.copy()
            del evt['title']
            response = self.app.put(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'title'")

        # TODO: test unauthorized user
        with self.subTest("fails when the client is not authorized"):
            response = self.app.put(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)
        # pass
    
    @skip("Unimplemented test")
    def test_delete(self):
        # TODO: test success
        # TODO: test invalid id
        # TODO: test invalid data
        # TODO: test unauthorized user
        pass
