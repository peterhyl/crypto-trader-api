import os
import unittest


class BackendTestCase(unittest.TestCase):

    db_path = 'sqlite:///'

    def setUp(self):
        # creates a test client
        os.environ['FLASK_ENV'] = 'test'
        os.environ['DATABASE_URL'] = self.db_path

        from app import create_app

        app = create_app()
        self.app = app.test_client()

    def test_app_env(self):
        self.assertTrue(self.app.application.config['TESTING'])
        self.assertFalse(self.app.application.config['DEBUG'])
        self.assertEqual(self.app.application.config['SQLALCHEMY_DATABASE_URI'], self.db_path)

    def test_page_not_found(self):
        result = self.app.post('/')

        self.assertEqual(result.status_code, 404)

    def test_api(self):
        data = {'name': 'testexchange', 'currency_shortcut': 'TET', 'currency_name': 'test'}
        subset = set({'shortcut': 'TET', 'name': 'test'}.items())
        result = self.app.post('/api/v1/crypto/exchanges', json=data)

        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json['name'], data['name'])
        self.assertTrue(subset.issubset(set(result.json['currency'][0].items())))

        exchange_id = result.json["id"]

        # ----------------------------- Deposit -----------------------------
        data = {'amount': 11.9}
        result = self.app.post(f'/api/v1/crypto/exchanges/{exchange_id}', json=data)

        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json, {'status': 'success'})

        # ----------------------------- Currencies -----------------------------
        data = [{'method': 'POST', 'currency': {'name': 'foo', 'shortcut': 'FOO', 'actual_rate': 1.2}},
                {'method': 'POST', 'currency': {'name': 'boo', 'shortcut': 'BOO', 'actual_rate': 1.3}}]
        result = self.app.put(f'/api/v1/crypto/exchanges/{exchange_id}/currencie', json=data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json), 3)

        data = [{'method': 'PUT', 'currency': {'id': 3, 'name': 'meh', 'shortcut': 'BOO', 'actual_rate': 1.5}},
                {'method': 'DELETE', 'currency': {'id': 2}}]
        result = self.app.put(f'/api/v1/crypto/exchanges/{exchange_id}/currencie', json=data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json), 2)

        # ----------------------------- Trade -----------------------------
        data = {'amount': 4.2, 'currency_in': 'TET', 'currency_out': 'BOO'}
        result = self.app.post(f'/api/v1/crypto/exchanges/{exchange_id}/trades', json=data)

        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json, {'status': 'success'})

        # ----------------------------- History -----------------------------
        result = self.app.get(f'/api/v1/crypto/history')

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json), 1)

        result = self.app.get(f'/api/v1/crypto/history?offset=1')

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json), 0)

    def test_failure(self):
        from app.errors.exceptions import BackendError
        data = {'name': 'testexchange', 'currency_shortcut': 'TT', 'currency_name': 'test'}
        result = self.app.post('/api/v1/crypto/exchanges', json=data)

        self.assertEqual(result.status_code, 400)
        self.assertRaises(ValueError)

        data = {'amount': 11.9}
        result = self.app.post(f'/api/v1/crypto/exchanges/33', json=data)

        self.assertEqual(result.status_code, 400)
        self.assertRaises(BackendError)

        # unimplemented method GET
        result = self.app.get('/api/v1/crypto/exchanges', json=data)

        self.assertEqual(result.status_code, 400)


if __name__ == '__main__':
    unittest.main()
