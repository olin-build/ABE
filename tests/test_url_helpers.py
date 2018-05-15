import unittest

from abe.helper_functions.url_helpers import url_add_query_params


class UrlHelpersTestCase(unittest.TestCase):

    def test_url_add_query_params(self):
        self.assertEqual(url_add_query_params("http://localhost:3000"),
                         "http://localhost:3000")
        self.assertEqual(url_add_query_params("http://localhost:3000/path"),
                         "http://localhost:3000/path")
        self.assertEqual(url_add_query_params("http://localhost:3000/path?q=1"),
                         "http://localhost:3000/path?q=1")
        self.assertEqual(url_add_query_params("http://localhost:3000/path", a=1),
                         "http://localhost:3000/path?a=1")
        self.assertEqual(url_add_query_params("http://localhost:3000/path?q=1", a=2),
                         "http://localhost:3000/path?q=1&a=2")
        self.assertEqual(url_add_query_params("http://localhost:3000/path?q=1&r=2", a=3, b=4),
                         "http://localhost:3000/path?q=1&r=2&a=3&b=4")
        self.assertEqual(url_add_query_params("http://localhost:3000/path?q=1&#frag", a=2),
                         "http://localhost:3000/path?q=1&a=2#frag")
