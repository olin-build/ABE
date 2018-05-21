#!/usr/bin/env python3
"""Test the auth helpers.
"""
import os
import unittest

from werkzeug.exceptions import HTTPException

from . import app  # noqa: F401

# This import must occur after `from . import` sets the environment variables
from abe import auth   # isort:skip


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.intranet_cdirs = os.environ["INTRANET_CDIRS"]

    def tearDown(self):
        os.environ["INTRANET_CDIRS"] = self.intranet_cdirs
        auth.reload_env_vars()

    def test_intranet_ips(self):
        os.environ['INTRANET_CDIRS'] = '127.0.0.1/24'
        auth.reload_env_vars()
        assert auth.ip_inside_intranet('127.0.0.1')
        assert auth.ip_inside_intranet('127.0.0.10')
        assert not auth.ip_inside_intranet('127.0.1.0')
        assert not auth.ip_inside_intranet('192.0.0.1')

        os.environ['INTRANET_CDIRS'] = '127.0.0.1,192.0.0.1/16'
        auth.reload_env_vars()
        assert auth.ip_inside_intranet('127.0.0.1')
        assert not auth.ip_inside_intranet('127.0.0.10')
        assert auth.ip_inside_intranet('192.0.0.1')
        assert auth.ip_inside_intranet('192.0.1.1')
        assert auth.ip_inside_intranet('192.0.255.1')
        assert not auth.ip_inside_intranet('192.1.0.1')

    def test_intranet_ips_v5(self):
        os.environ['INTRANET_CDIRS'] = '127.0.0.1/24,2001:0db8::/32'
        auth.reload_env_vars()
        assert auth.ip_inside_intranet('127.0.0.1')
        assert auth.ip_inside_intranet('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        assert not auth.ip_inside_intranet('2001:0db9:85a3:0000:0000:8a2e:0370:7334')

    def test_require_scope(self):
        os.environ['INTRANET_CDIRS'] = '127.0.0.1/24'
        auth.reload_env_vars()

        @auth.require_scope('edit:events')
        def route():
            return 'ok'

        with self.subTest("permits a whitelisted IP"):
            with app.test_request_context('/', environ_base={'REMOTE_ADDR': '127.0.0.1'}):
                assert route() == 'ok'

        with self.subTest("denies a non-whitelisted IP"):
            with app.test_request_context('/', environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                with self.assertRaises(HTTPException) as http_error:
                    route()
                self.assertEqual(http_error.exception.code, 401)

        with self.subTest("reads the client IP instead of the proxy"):
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

        with self.subTest("detects attempt to spoof the client IP"):
            with app.test_request_context('/',
                                          headers={'X-Forwarded-For': '127.0.0.1,192.168.0.1'}):
                with self.assertRaises(HTTPException) as http_error:
                    route()

        # Test auth cookie
        with self.subTest("off-whitelist IP, no cookie"):
            with app.test_request_context('/', environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                with self.assertRaises(HTTPException) as http_error:
                    route()
                self.assertEqual(http_error.exception.code, 401)

        with self.subTest("off-whitelist IP, correct cookie"):
            with app.test_request_context('/', headers={"COOKIE": f"access_token={auth.create_access_token()}"},
                                          environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                assert route() == 'ok'

        with self.subTest("off-whitelist IP, incorrect cookie"):
            with app.test_request_context('/', headers={"COOKIE": "access_token=invalid-token"},
                                          environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                with self.assertRaises(HTTPException) as http_error:
                    route()
                self.assertEqual(http_error.exception.code, 401)

        with self.subTest("off-whitelist IP, authorization header"):
            with app.test_request_context('/', headers={"Authorization": f"Bearer {auth.create_access_token()}"},
                                          environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                assert route() == 'ok'

            with app.test_request_context('/', headers={"Authorization": "Bearer invalid-token"},
                                          environ_base={'REMOTE_ADDR': '127.0.1.1'}):
                with self.assertRaises(HTTPException) as http_error:
                    route()
                self.assertEqual(http_error.exception.code, 401)
