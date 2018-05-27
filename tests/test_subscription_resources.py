from . import abe_unittest, app, db

# This import must occur after `from . import` sets the environment variables
from abe.resource_models.subscription_resources import SubscriptionAPI, SubscriptionICS  # isort:skip


class SubscriptionAPITestCase(abe_unittest.TestCase):

    def setUp(self):
        self.resource = SubscriptionAPI()
        data = {
            'sid': 'test-id',
            'labels': ['library'],
        }
        db.Subscription(**data).save()

    def test_get(self):
        with self.subTest('valid subscription id'):
            ics = self.resource.get('test-id')
            self.assertEqual(ics['id'], 'test-id')
            self.assertEqual(ics['labels'], ['library'])
            self.assertEqual(ics['ics_url'], '/subscriptions/test-id/ics')

        with self.subTest('invalid subscription id'):
            msg, error_code = self.resource.get('invalid-id')
            self.assertIsInstance(msg, str)
            self.assertEqual(error_code, 404)

    def test_post(self):
        with self.subTest('new subscription'):
            data = {
                'labels': ['library'],
            }
            with app.test_request_context(data=data):
                ics = self.resource.post()
            assert len(db.Subscription.objects(sid=ics['id'])) == 1
            self.assertEqual(ics['labels'], ['library'])

    def test_put(self):
        data = {
            'labels': ['featured'],
        }
        with app.test_request_context(data=data):
            ics = self.resource.put('test-id')
        assert ics['labels'] == ['featured']
        assert db.Subscription.objects(sid='test-id').first().labels == ['featured']


class SubscriptionICSTestCase(abe_unittest.TestCase):

    def setUp(self):
        self.resource = SubscriptionICS()
        data = {
            'sid': 'test-id',
            'labels': ['library'],
        }
        db.Subscription(**data).save()

    def test_get(self):
        with app.test_request_context():
            res = self.resource.get('test-id')
        assert res.mimetype == 'text/calendar'
        self.assertRegex(res.headers['Content-Disposition'], r'attachment;filename=.+\.ics')
        self.assertRegex(res.response[0].decode(), r'(?s)BEGIN:VCALENDAR.+END:VCALENDAR\s*$')

        with app.test_request_context():
            _, response_code = self.resource.get('invalid-id')
        assert response_code == 404
