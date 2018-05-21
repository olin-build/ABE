import re
import unittest
from urllib.parse import parse_qsl, urlparse

import flask

from . import app, user_access_token


class AdminTestCase(unittest.TestCase):

    def test_login(self):
        client = app.test_client()

        with self.subTest("redirects to oauth"):
            response = client.get('/login')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(re.sub(r'\?.*', '', response.location), 'http://localhost/oauth/authorize')
            params = dict(parse_qsl(urlparse(response.location).query))
            self.assertEqual(params['redirect_uri'], '/login/token')
            self.assertEqual(params['response_type'], 'token')
            self.assertRegex(params['state'], r'[^.]+.[^.]+')

        with self.subTest("handles redirection from oauth"):
            token = user_access_token
            url = f"{params['redirect_uri']}?state={params['state']}&access_token={token}"
            response = client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, 'http://localhost/account/info')

        with self.subTest("sets authorization"):
            response = client.get('/user/',
                                  headers={'X-Forwarded-For': '127.0.1.1'})
            self.assertEqual(response.status_code, 200)
            user = flask.json.loads(response.data)
            self.assertEqual(user['authenticated'], True)
            self.assertEqual(user['provider'], 'test')
