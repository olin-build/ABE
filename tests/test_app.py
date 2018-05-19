#!/usr/bin/env python3
"""The world's leading test suite for ABE
This test suite requires a local mongodb instance and writes to/drops a
database named "abe-unittest" for testing.
"""
import flask

from . import abe_unittest, admin_access_token, app, sample_data


class AbeTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        app.debug = True  # enable debug to prevent https redirects
        self.client = app.test_client()

    def test_empty_db(self):
        event_response = self.client.get('/events/')
        label_response = self.client.get('/labels/')
        assert flask.json.loads(event_response.data) == []
        assert flask.json.loads(label_response.data) == []

    def test_add_sample_events(self):
        """Adds the sample events to the database"""
        for event in sample_data.load_sample_data().events:
            response = self.client.post(
                '/events/',
                data=flask.json.dumps(event),  # use flask.json for datetimes
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 201)  # check only status code

    def test_import_ics(self):
        """Imports an ICS feed by URL"""
        for feed in sample_data.load_sample_data().icss:
            response = self.client.post('/ics/', data=flask.json.dumps(feed), content_type='application/json')
            self.assertEqual(response.status_code, 200)

    def test_add_sample_labels(self):
        """Adds the sample labels to the database"""
        for event in sample_data.load_sample_data().labels:
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(event),
                content_type='application/json',
                headers={'Authorization': f"Bearer {admin_access_token}"}
            )
            self.assertEqual(response.status_code, 201)
