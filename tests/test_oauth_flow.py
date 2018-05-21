import re
import unittest
from urllib.parse import parse_qsl, quote_plus, unquote_plus, urlparse

from abe.helper_functions import url_parse_fragment_params

from . import app


class OAuthTestCase(unittest.TestCase):

    def test_implicit_grant(self):
        client = app.test_client()
        response = client.get('/oauth/authorize' +
                              '?redirect_uri=' + quote_plus('https://client/callback') +
                              '&response_type=token' +
                              '&state=initial-state',
                              )
        self.assertEqual(response.status_code, 200)

        with self.subTest("responds with a link"):
            html = response.data.decode()
            href_re = r'<a id="slack-oauth-link"\s+(?:[^>]*)\bhref="(.+?)">'
            self.assertRegex(html, href_re)
            slack_url = urlparse(re.search(href_re, html)[1])
            self.assertEqual(slack_url.netloc, 'slack.com')
            self.assertEqual(slack_url.path, '/oauth/authorize')

        with self.subTest("…with valid query parameters"):
            query = dict(parse_qsl(slack_url.query))
            self.assertEqual(query['client_id'], 'slack-oauth-client-id')
            self.assertEqual(unquote_plus(query['redirect_uri']),
                             'http://localhost/oauth/slack?redirect_uri=https://client/callback')

        with self.subTest("calling the Slack callback URI"):
            response = client.get('/oauth/slack' +
                                  '?redirect_uri=https://client/callback'
                                  '&state=' + quote_plus(query['state'])
                                  )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(re.sub(r'#.*', '', response.location), 'https://client/callback')
            # redirect_uri = urlparse(response.location)
            # params = dict(s.split('=', 2) for s in redirect_uri.fragment.split('&'))
            params = url_parse_fragment_params(response.location)
            self.assertEqual(params['token_type'], 'bearer')
            self.assertEqual(params['state'], 'initial-state')
            self.assertRegex(params['access_token'], r'.+')
            self.assertRegex(params['expires_in'], r'\d+')
