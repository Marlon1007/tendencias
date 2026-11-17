import unittest
from unittest.mock import patch

import psycopg
import app as application


class AppTests(unittest.TestCase):
    def setUp(self):
        application.app.config['TESTING'] = True
        self.client = application.app.test_client()

    def test_lists_messages_and_escapes_html(self):
        with patch('app.get_connection') as connect:
            connect.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [
                (2, '<script>alert(1)</script>'), (1, 'Hola Ecuador')
            ]
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hola Ecuador', response.data)
        self.assertIn(b'&lt;script&gt;', response.data)
        self.assertNotIn(b'<script>', response.data)
        self.assertIn(b'name="content"', response.data)

    def test_saves_text_using_parameters_then_redirects(self):
        text = "Hola '); DROP TABLE messages; --"
        with patch('app.get_connection') as connect:
            response = self.client.post('/', data={'content': text})
            connection = connect.return_value.__enter__.return_value
            connection.execute.assert_called_once_with(
                'INSERT INTO messages (content) VALUES (%s)', (text,)
            )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/')

    def test_rejects_empty_text_without_database_access(self):
        with patch('app.get_connection') as connect:
            for data in ({}, {'content': ''}, {'content': '   '}):
                with self.subTest(data=data):
                    self.assertEqual(self.client.post('/', data=data).status_code, 400)
            connect.assert_not_called()

    def test_database_failure_returns_generic_error(self):
        with patch('app.get_connection', side_effect=psycopg.OperationalError('private-details')):
            for method in (lambda: self.client.get('/'),
                           lambda: self.client.post('/', data={'content': 'Hola'})):
                response = method()
                self.assertEqual(response.status_code, 503)
                self.assertNotIn(b'private-details', response.data)


if __name__ == '__main__':
    unittest.main()
