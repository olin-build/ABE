import os
from importlib import reload

import flask

from . import abe_unittest
from .context import abe  # noqa: F401

# These imports have to happen after .context sets the environment variables
from abe.app import app  # isort:skip
from abe import auth  # isort:skip # noqa: F401


class AccountTestCase(abe_unittest.TestCase):

    def setUp(self):
        global auth
        super().setUp()
        # self.app = app.test_client(use_cookies=False)
        os.environ['INTRANET_CDIRS'] = "127.0.0.1/24"
        reload(auth)

    def test_unauthorized_client(self):
        client = app.test_client()
        response = client.get(
            '/account/',
            content_type='application/json',
            headers={'X-Forwarded-For': '192.168.1.1'}
        )
        self.assertEqual(response.status_code, 200)
        account = flask.json.loads(response.data)
        self.assertEqual(account['authenticated'], False)
        self.assertEqual(account['permissions'], [])
        self.assertEqual(account['scope'], [])

    def test_authorized_client(self):
        client = app.test_client()
        response = client.get(
            '/account/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        account = flask.json.loads(response.data)
        self.assertEqual(account['authenticated'], True)
        self.assertEqual(set(account['permissions']), {'add_events', 'edit_events', 'view_all_events'})
        self.assertEqual(set(account['scope']), {'events:create', 'events:edit', 'community_events:read'})
