#!/usr/bin/env python3
"""The world's leading test suite for ABE
This test suite requires a local mongodb instance and writes to/drops a
database named "abe-unittest" for testing.
"""
import os
import unittest

import flask
from pymongo import MongoClient

from abe import sample_data

from . import abe_unittest
from .context import abe  # noqa: F401


class AbeTestCase(abe_unittest.TestCase):

    def setUp(self):
        """Setup testing environment"""
        os.environ["DB_NAME"] = "abe-unittest"
        os.environ["MONGO_URI"] = ""
        import abe.app  # import abe after env so it inits correctly
        abe.app.app.debug = True  # enable debug to prevent https redirects
        self.app = abe.app.app.test_client()

    def tearDown(self):
        """Teardown testing environment"""
        client = MongoClient()
        client.drop_database(os.environ['DB_NAME'])  # remove testing db
        client.close()

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
            assert response._status_code == 201  # check only status code

    def test_add_sample_labels(self):
        """Adds the sample labels to the database"""
        for event in sample_data.load_sample_data().labels:
            response = self.app.post(
                '/labels/',
                data=flask.json.dumps(event),
                content_type='application/json'
            )
            assert response._status_code == 201

    def test_date_range(self):
        from abe import database as db
        sample_data.load_data(db)

        with self.subTest("a six-month query returns some events"):
            response = self.app.get('/events/?start=2017-01-01&end=2017-07-01')
            self.assertEqual(response._status_code, 200)
            self.assertEqual(len(flask.json.loads(response.data)), 25)

        with self.subTest("a one-year query returns all events"):
            response = self.app.get('/events/?start=2017-01-01&end=2018-01-01')
            assert response._status_code == 200, f"status={response._status_code}"
            self.assertEqual(len(flask.json.loads(response.data)), 69)

        with self.subTest("a two-year query is too long"):
            response = self.app.get('/events/?start=2017-01-01&end=2019-01-01')
            # FIXME:
            self.assertEqual(response._status_code, 404)

        with self.subTest("a one-year query works for leap years"):
            response = self.app.get('/events/?start=2020-01-01&end=2021-01-01')
            # FIXME:
            self.assertEqual(response._status_code, 200)


if __name__ == '__main__':
    unittest.main()
