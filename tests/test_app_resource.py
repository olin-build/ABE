from werkzeug.exceptions import BadRequest, NotFound

from . import abe_unittest, admin_access_token, app

# These imports must occur after `from . import` sets the environment variables
from abe.document_models import App  # isort:skip
from abe.resource_models.app_resources import AppApi   # isort:skip


class AppsResourceTestCase(abe_unittest.TestCase):

    def setUp(self):
        self.client_id = App.admin_app().client_id
        self.headers = {
            'Authorization': f'Bearer {admin_access_token}',
        }

    def test_get(self):
        resource = AppApi()
        with app.test_request_context(headers=self.headers):
            response = resource.get()
        self.assertEqual(len(response), 1)
        client_app, = response
        self.assertEqual(client_app['name'], "ABE Admin")
        self.assertEqual(client_app['client_id'], self.client_id)
        self.assertRegex(client_app['client_id'], r'[0-9a-f]+')

    def test_get_id(self):
        resource = AppApi()
        with app.test_request_context(headers=self.headers):
            response = resource.get()
        self.assertEqual(len(response), 1)
        client_app, = response
        self.assertEqual(client_app['name'], "ABE Admin")

    def test_post(self):
        resource = AppApi()
        app_count = len(App.objects)
        data = {'name': "Test App"}
        with app.test_request_context(data=data, headers=self.headers):
            client_app, response_code, *_ = resource.post()
        self.assertEqual(response_code, 201)
        self.assertEqual(client_app['name'], 'Test App')
        self.assertRegex(client_app['client_id'], r'[0-9a-f]+')
        self.assertEqual(len(App.objects), app_count + 1)

    def test_put(self):
        resource = AppApi()
        data = {'name': "Renamed App"}
        with app.test_request_context(data=data, headers=self.headers):
            client_app = resource.put(self.client_id)
        self.assertEqual(client_app['name'], 'Renamed App')

        data = {'client_id': "spoofed client id"}
        with app.test_request_context(data=data, headers=self.headers):
            with self.assertRaises(BadRequest):
                client_app = resource.put(self.client_id)

    def test_delete(self):
        resource = AppApi()
        app_count = len(App.objects)
        with app.test_request_context(headers=self.headers):
            client_app = resource.delete(self.client_id)
        self.assertEqual(client_app['client_id'], self.client_id)
        self.assertEqual(len(App.objects), app_count - 1)

        with self.subTest("fails on an invalid id"):
            with app.test_request_context(headers=self.headers):
                with self.assertRaises(NotFound):
                    resource.delete(self.client_id)
