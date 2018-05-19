from unittest import skip

from . import abe_unittest

# This import must occur after .context sets the environment variables
from abe.resource_models import subscription_resources  # isort:skip


class SubscriptionAPITestCase(abe_unittest.TestCase):

    def setUp(self):
        self.resource = subscription_resources.SubscriptionAPI()
        # TODO: populate the database with a dummy subscription object
        # that we can test against below

    def test_get(self):
        with self.subTest('valid subscription id'):
            self.skipTest('Unimplemented test')
            # TODO: test this
            # ics, status = self.resource.get('test-id')
            # self.assertEqual(msg, None)
            # self.assertEqual(error_code, 200)

        with self.subTest('valid subscription id'):
            msg, error_code = self.resource.get('invalid-id')
            self.assertIsInstance(msg, str)
            self.assertEqual(error_code, 404)

    def test_post(self):
        with self.subTest('new subscription'):
            self.skipTest('Unimplemented test')
            pass
            # msg, status = self.resource.post('new-id')

        with self.subTest('duplicate id'):
            self.skipTest('Unimplemented test')
            pass
            # msg, status = self.resource.get('test-id')

    skip('Unimplemented test')

    def test_put(self):
        pass
        # TODO: update labels
        # TODO: validation error
        # TODO: invalid subscription id


class SubscriptionICSTestCase(abe_unittest.TestCase):

    def setUp(self):
        self.resource = subscription_resources.SubscriptionICS()

    @skip('Unimplemented test')
    def test_get(self):
        pass
        # TODO: get
        # TODO: manual labels
        # TODO: invalid subscription id
