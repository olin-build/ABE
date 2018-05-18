import flask

from . import abe_unittest
from .context import app, sample_data

from abe.auth import create_auth_token  # isort:skip


class LabelsTestCase(abe_unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.client = app.test_client()
        sample_data.load_data(self.db)
        token = create_auth_token(role='admin')
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_label_by_id(self, id):
        response = self.client.get('/labels/')
        self.assertEqual(response.status_code, 200)
        return next(label for label in flask.json.loads(response.data)
                    if label['id'] == id)

    def get_label_by_name(self, name):
        response = self.client.get('/labels/')
        self.assertEqual(response.status_code, 200)
        return next(label for label in flask.json.loads(response.data)
                    if label['name'] == name)

    def test_get(self):
        response = self.client.get('/labels/')
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
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(label1),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 201)

        with self.subTest("fails on a duplicate label name"):
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(label1),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 400)

        with self.subTest("fails when fields are missing"):
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps({}),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 400)
            self.assertRegex(flask.json.loads(response.data)['error_message'], r"^ValidationError.*'name'")

    def test_post_auth(self):
        label_noauth = {
            'name': 'label-test-notauth',
        }
        label_success = {
            'name': 'label-test-success',
        }
        with self.subTest("fails on an unauthenticated client"):
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(label_noauth),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 401)

        with self.subTest("fails on an unauthorized client"):
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(label_noauth),
                content_type='application/json',
                headers={'Authorization': f'Bearer {create_auth_token()}'}
            )
            self.assertEqual(response.status_code, 401)

        with self.subTest("succeeds on an authorized client"):
            response = self.client.post(
                '/labels/',
                data=flask.json.dumps(label_success),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 201)

    def test_put(self):
        # TODO: test w/ invalid id
        # TODO: test w/ invalid data

        label_id = self.get_label_by_name('library')['id']
        label_data = {
            'description': 'New description',
        }

        with self.subTest("fails on an un-authenticated client"):
            response = self.client.put(
                '/labels/' + label_id,
                data=flask.json.dumps(label_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 401)

        with self.subTest("succeeds on an authorized client"):
            response = self.client.put(
                '/labels/' + label_id,
                data=flask.json.dumps(label_data),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 200)
            label = self.get_label_by_id(label_id)
            self.assertEqual(label['description'], 'New description')

        with self.subTest("fails no invalid data"):
            response = self.client.put(
                '/labels/' + label_id,
                data=flask.json.dumps({'colorx': 'invalid-color'}),
                content_type='application/json',
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 400)

    def test_put_name(self):
        events_path = '/events/?start=2017-01-01&end=2018-01-01'
        library_events = sum('library' in event['labels']
                             for event in flask.json.loads(self.client.get(events_path).data))
        self.assertGreater(library_events, 20)

        label_id = self.get_label_by_name('library')['id']
        response = self.client.put(
            '/labels/' + label_id,
            data=flask.json.dumps({'name': 'renamed'}),
            content_type='application/json',
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)

        with self.subTest("updates label.name"):
            self.assertEqual(self.get_label_by_id(label_id)['name'], 'renamed')

        with self.subTest("updates event.labels lists"):
            events = flask.json.loads(self.client.get(events_path).data)
            unrenamed_events = sum('library' in event['labels'] for event in events)
            renamed_events = sum('renamed' in event['labels'] for event in events)
            self.assertEqual(unrenamed_events, 0)
            self.assertEqual(renamed_events, library_events)

    def test_delete(self):
        # TODO: test success
        # TODO: test invalid id
        # TODO: test invalid data

        with self.subTest("fails when the client is not authorized"):
            response = self.client.delete(
                '/labels/library',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            self.assertEqual(response.status_code, 401)
