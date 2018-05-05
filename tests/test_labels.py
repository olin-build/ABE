import flask

from . import abe_unittest
from .context import abe  # noqa: F401

# These imports have to happen after .context sets the environment variables
import abe.app  # isort:skip
from abe import sample_data  # isort:skip


class LabelsTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.app = abe.app.app.test_client()
        sample_data.load_data(self.db)

    def test_get(self):
        response = self.app.get('/labels/')
        self.assertEqual(response.status_code, 200)
        labels = flask.json.loads(response.data)
        self.assertEqual(len(labels), 15)
        label = next((l for l in labels if l['name'] == 'library'), None)
        self.assertIsNotNone(label)
        self.assertEqual(label['name'], 'library')
        self.assertEqual(label['color'], '#26AAA5')
        self.assertRegex(label['description'], r'relating to the Olin Library')
        self.assertEqual(label['url'], 'http://library.olin.edu/')

    def test_post(self):
        label1 = {
            'name': 'label-test',
        }
        with self.subTest("succeeds when required fields are present"):
            response = self.app.post(
                '/labels/',
                data=flask.json.dumps(label1),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

        # FIXME:
        # with self.subTest("fails on a duplicate label name"):
        #     response = self.app.post(
        #         '/labels/',
        #         data=flask.json.dumps(label1),
        #         content_type='application/json'
        #     )
        #     self.assertEqual(response.status_code, 400)

        with self.subTest("fails when fields are missing"):
            response = self.app.post(
                '/labels/',
                data=flask.json.dumps({}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'name'")

        with self.subTest("fails when the client is not authorized"):
            label = {
                'name': 'label-test-2',
            }
            response = self.app.post(
                '/labels/',
                data=flask.json.dumps(label),
                content_type='application/json',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)

    def test_put(self):
        # TODO: test success
        # TODO: test invalid id
        # TODO: test invalid data
        with self.subTest("fails when the client is not authorized"):
            response = self.app.put(
                '/labels/library',
                data=flask.json.dumps({'description': 'new description'}),
                content_type='application/json',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)

    def test_delete(self):
        # TODO: test success
        # TODO: test invalid id
        # TODO: test invalid data
        with self.subTest("fails when the client is not authorized"):
            response = self.app.delete(
                '/labels/library',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)
