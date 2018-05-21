from unittest import skip

import flask
import isodate

from . import abe_unittest, app, db, sample_data


class EventsTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.client = app.test_client()
        sample_data.load_data(db)

    def test_get_events(self):
        with self.subTest("a six-month query returns some events"):
            response = self.client.get('/events/?start=2017-01-01&end=2017-07-01')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(flask.json.loads(response.data)), 25)

        with self.subTest("a one-year query returns all events"):
            response = self.client.get('/events/?start=2017-01-01&end=2018-01-01')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(flask.json.loads(response.data)), 69)

        with self.subTest("a two-year query is too long"):
            response = self.client.get('/events/?start=2017-01-01&end=2019-01-01')
            self.assertEqual(response.status_code, 404)

        with self.subTest("a one-year query works for leap years"):
            response = self.client.get('/events/?start=2020-01-01&end=2021-01-01')
            self.assertEqual(response.status_code, 200)

        with self.subTest("an unauthenticated sender retrieves only public events"):
            event_response = self.client.get('/events/?start=2017-01-01&end=2017-07-01')
            # TODO: change the following when #75 is implemented
            self.assertEqual(len(flask.json.loads(event_response.data)), 25)

    def test_post(self):
        event = {
            'title': 'test_post',
            'start': isodate.parse_datetime('2018-05-04T09:00:00')
        }

        with self.subTest("succeeds when required fields are present"):
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

        with self.subTest("fails on missing fields"):
            evt = event.copy()
            del evt['title']
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'title'")

            evt = event.copy()
            del evt['start']
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'start'")

        with self.subTest("fails on invalid fields"):
            evt = event.copy()
            evt['invalid'] = 'invalid field'
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails on invalid field values"):
            evt = event.copy()
            evt['url'] = 'invalid field value'
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(evt),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails if event has protected label"):
            event = {
                'title': 'protected post',
                'start': isodate.parse_datetime('2018-05-10T09:00:00'),
                'labels': ["StAR"]
            }
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    def test_post_auth(self):
        event = {
            'title': 'test_post',
            'start': isodate.parse_datetime('2018-05-04T09:00:00')
        }
        with self.subTest("fails when the client is not yet authorized"):
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={
                    'X-Forwarded-For': '192.168.1.1',
                }
            )
            self.assertEqual(response.status_code, 401)

        with self.subTest("succeeds when required fields are present"):
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            # TODO: test that the event is in the database

        with self.subTest("succeeds due to auth cookie"):
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={
                    'X-Forwarded-For': '192.168.1.1',
                }
            )
            self.assertEqual(response.status_code, 201)

    def test_put(self):
        # TODO: test unauthorized user
        response = self.client.get('/events/?start=2017-01-01&end=2017-07-01')
        self.assertEqual(response.status_code, 200)
        event_id = flask.json.loads(response.data)[0]['id']

        with self.subTest("succeeds on valid id"):
            response = self.client.put(
                f'/events/{event_id}',
                data=flask.json.dumps({'title': 'new title'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            # TODO: test that the event has a new value

        with self.subTest("fails on invalid id"):
            response = self.client.put(
                f'/events/{event_id}x',
                data=flask.json.dumps({'title': 'new title'}),
                content_type='application/json'
            )
            # FIXME: why is this not 404?
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails on invalid field"):
            response = self.client.put(
                f'/events/{event_id}',
                data=flask.json.dumps({'invalid_field': 'value'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails on invalid field value"):
            response = self.client.put(
                f'/events/{event_id}',
                data=flask.json.dumps({'url': 'invalid url'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

        # This exercises a different code path in mongodb -> JOSN error conversion
        with self.subTest("fails on multiple invalid fields"):
            response = self.client.put(
                f'/events/{event_id}',
                data=flask.json.dumps({'invalid_field-1': 'value',
                                       'invalid_field-2': 'value'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails if event is protected"):
            response = self.client.get('/events/?start=2018-05-30&end=2018-05-31')
            self.assertEqual(response.status_code, 200)
            event_id = flask.json.loads(response.data)[0]['id']
            response = self.client.put(
                f'/events/{event_id}',
                data=flask.json.dumps({'title': 'new title'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    @skip("Unimplemented test")
    def test_delete(self):
        # TODO: test success
        # TODO: test invalid id
        # TODO: test invalid data
        # TODO: test unauthorized user
        pass
