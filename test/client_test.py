import os.path
import sys
import unittest
import traceback

import six
from six.moves import urllib

from errbit_reporter import Configuration, Client, Notice


class FakeResponse(object):
    def __init__(self, body):
        self.body_file = six.BytesIO(body)
        self.code = 200
        self.msg = "OK"
        self.headers = {}

    def info(self):
        return self.headers

    def read(self):
        return self.body_file.read()

    def close(self):
        self.body_file.close()


class TestHandler(urllib.request.HTTPHandler):
    request = None
    response = None
    response_filename = os.path.join(os.path.dirname(__file__), 'fixtures', 'response.xml')

    def do_open(self, http_class, request, **http_conn_args):
        cls = self.__class__
        cls.request = request
        return cls.response

opener = urllib.request.build_opener(TestHandler)
urllib.request.install_opener(opener)


class ClientTest(unittest.TestCase):
    def setUp(self):
        response_filename = os.path.join(os.path.dirname(__file__), 'fixtures', 'response.xml')
        with open(response_filename, 'rb') as f:
            body = f.read()
        TestHandler.response = FakeResponse(body)

        self.config = Configuration('apikey', 'http://localhost')
        self.client = Client(self.config)

    def tearDown(self):
        TestHandler.request = None
        TestHandler.response = None

    def test_notify(self):
        try:
            int('a')
        except Exception:
            expected_body = Notice.from_exception(self.config, sys.exc_info()).serialize()
            metadata = self.client.notify()
        self.assertEqual(TestHandler.request.get_full_url(), "http://localhost/notifier_api/v2/notices/")
        self.assertEqual(TestHandler.request.get_method(), "POST")
        self.assertEqual(TestHandler.request.data, expected_body)
        self.assertEqual(metadata.id, '87186dda0c1d88569a171698')
        self.assertEqual(metadata.err_id, '7eafc85735047f2e5c9272b7')
        self.assertEqual(metadata.problem_id, '4886aba098109edbeb67a7f0')

    def test_notify_on_exception(self):
        inner_exc_info = None
        try:
            with self.client.notify_on_exception():
                try:
                    int('a')
                except Exception:
                    inner_exc_info = sys.exc_info()
                    raise
        except Exception:
            self.assertEqual(sys.exc_info(), inner_exc_info)

        self.assertEqual(TestHandler.request.get_full_url(), "http://localhost/notifier_api/v2/notices/")
        self.assertEqual(TestHandler.request.get_method(), "POST")
        filename, line_number, function_name, text = traceback.extract_tb(inner_exc_info[2])[0]
        top_frame = '<line file="%s" method="%s" number="%d" />' % (filename, function_name, line_number)
        self.assertIn(top_frame.encode('utf-8'), TestHandler.request.data)

if __name__ == '__main__':
    unittest.main()
