#!/usr/bin/env python3
"""Test the auth helpers.
"""
import os
import unittest
from importlib import reload

import flask
from werkzeug.exceptions import HTTPException

from abe import auth  # noqa: F401

app = flask.Flask(__name__)


class AuthTestCase(unittest.TestCase):

    def test_intranet_ips(self):
        global auth
        os.environ['INTRANET_IPS'] = '127.0.0.1/24'
        auth = reload(auth)
        assert '127.0.0.1' in auth.INTRANET_IPS
        assert '127.0.0.10' in auth.INTRANET_IPS
        assert '127.0.1.0' not in auth.INTRANET_IPS
        assert '192.0.0.1' not in auth.INTRANET_IPS

        os.environ['INTRANET_IPS'] = '127.0.0.1,192.0.0.1/16'
        auth = reload(auth)
        assert '127.0.0.1' in auth.INTRANET_IPS
        assert '127.0.0.10' not in auth.INTRANET_IPS
        assert '192.0.0.1' in auth.INTRANET_IPS
        assert '192.0.1.1' in auth.INTRANET_IPS
        assert '192.0.255.1' in auth.INTRANET_IPS
        assert '192.1.0.1' not in auth.INTRANET_IPS

    def test_intranet_ips_v5(self):
        global auth
        os.environ['INTRANET_IPS'] = '127.0.0.1/24,2001:0db8::/32'
        auth = reload(auth)
        assert '127.0.0.1' in auth.INTRANET_IPS
        assert '2001:0db8:85a3:0000:0000:8a2e:0370:7334' in auth.INTRANET_IPS
        assert '2001:0db9:85a3:0000:0000:8a2e:0370:7334' not in auth.INTRANET_IPS

    def test_edit_auth_required(self):
        global auth
        os.environ['INTRANET_IPS'] = '127.0.0.1/24'
        auth = reload(auth)

        @auth.edit_auth_required
        def route():
            return 'ok'

        with app.test_request_context('/', environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            assert route() == 'ok'
        with app.test_request_context('/', environ_base={'REMOTE_ADDR': '127.0.1.1'}):
            with self.assertRaises(HTTPException) as http_error:
                route()
            self.assertEqual(http_error.exception.code, 401)

        # Read the client IP instead of the Proxy
        with app.test_request_context('/', headers={'X-Forwarded-For': '127.0.0.1'}):
            assert route() == 'ok'
        with app.test_request_context('/', headers={'X-Forwarded-For': '127.0.0.255'}):
            assert route() == 'ok'
        with app.test_request_context('/',
                                      environ_base={'REMOTE_ADDR': '127.0.0.1'},
                                      headers={'X-Forwarded-For': '127.0.1.1'}):
            with self.assertRaises(HTTPException) as http_error:
                route()
            self.assertEqual(http_error.exception.code, 401)

        # Detect attempt to spoof the client IP.
        with app.test_request_context('/',
                                      headers={'X-Forwarded-For': '127.0.0.1,192.168.0.1'}):
            with self.assertRaises(HTTPException) as http_error:
                route()

        # Test auth cookie
        os.environ['SHARED_SECRET'] = 'security'
        auth = reload(auth)

        with app.test_request_context('/', headers={"COOKIE": "app_secret=security"},
                                      environ_base={'REMOTE_ADDR': '127.0.1.1'}):
            assert route() == 'ok'
        with app.test_request_context('/', headers={"COOKIE": "app_secret=obscurity"},
                                      environ_base={'REMOTE_ADDR': '127.0.1.1'}):
            with self.assertRaises(HTTPException) as http_error:
                route()
            self.assertEqual(http_error.exception.code, 401)
