import re
import unittest
import urllib.parse

import flask

from . import context  # noqa: F401

from abe.app import app  # isort:skip


class OAuthTestCase(unittest.TestCase):

    def test_oauth_flow(self):
        client = app.test_client()
        response = client.get('/oauth/authorize?redirect_uri=https://client/callback')
        self.assertEqual(response.status_code, 200)

        with self.subTest("returns HTML with a link"):
            html = response.data.decode()
            href_re = r'<a id="slack-oauth-link"\s+(?:[^>]*)\bhref="(.+?)">'
            self.assertRegexpMatches(html, href_re)
            slack_url = urllib.parse.urlparse(re.search(href_re, html)[1])
            self.assertEqual(slack_url.netloc, 'slack.com')
            self.assertEqual(slack_url.path, '/oauth/authorize')

        with self.subTest("…and valid query parameters"):
            query = dict(urllib.parse.parse_qsl(slack_url.query))
            self.assertEqual(query['client_id'], 'slack-oauth-client-id')
            self.assertEqual(urllib.parse.unquote_plus(query['redirect_uri']),
                             'http://localhost/oauth/slack?redirect_uri=https://client/callback')

        with self.subTest("…that contain a valid state"):
            state = flask.json.loads(query['state'])
            self.assertRegexpMatches(state['validation_code'], r'[0-9a-z-]+')
