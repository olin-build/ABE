import os

import flask

from . import app, abe_unittest

# This import must occur after .context sets the environment variables
from abe import auth  # isort:skip # noqa: F401


class AccountTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.intranet_cdirs = os.environ["INTRANET_CDIRS"]
        os.environ['INTRANET_CDIRS'] = "127.0.0.1/24"
        auth.reload_env_vars()

    def tearDown(self):
        os.environ["INTRANET_CDIRS"] = self.intranet_cdirs
        auth.reload_env_vars()

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
        scope = set(account['scope'])
        self.assertGreaterEqual(scope, {'events:create', 'events:edit', 'community_events:read'})
        self.assertGreaterEqual(scope, {'create:events', 'edit:events', 'delete:events'})
        self.assertGreaterEqual(scope, {'read:all_events'})
