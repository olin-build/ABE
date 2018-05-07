#!/usr/bin/env python3
"""The world's leading test suite for ABE
This test suite requires a local mongodb instance and writes to/drops a
database named "abe-unittest" for testing.
"""
import flask

from . import abe_unittest
from .context import abe  # noqa: F401

# These imports have to happen after .context sets the environment variables
import abe.app  # isort:skip
from abe import sample_data  # isort:skip


class AbeTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        abe.app.app.debug = True  # enable debug to prevent https redirects
        self.app = abe.app.app.test_client()

    def test_empty_db(self):
        event_response = self.app.get('/events/')
        label_response = self.app.get('/labels/')
        assert flask.json.loads(event_response.data) == []
        assert flask.json.loads(label_response.data) == []

    def test_add_sample_events(self):
        """Adds the sample events to the database"""
        for event in sample_data.load_sample_data().events:
            response = self.app.post(
                '/events/',
                data=flask.json.dumps(event),  # use flask.json for datetimes
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)  # check only status code

    def test_import_ics(self):
        """Imports an ICS feed by URL"""
        for feed in sample_data.load_sample_data().icss:
            respose = self.app.post('/ics/', data=flask.json.dumps(feed), content_type='application/json')
            self.assertEqual(respose.status_code, 200)

    def test_add_sample_labels(self):
        """Adds the sample labels to the database"""
        for event in sample_data.load_sample_data().labels:
            response = self.app.post(
                '/labels/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
