import os.path
import sys
import unittest

import six
from six.moves import urllib

from errbit_reporter.config import Configuration
from errbit_reporter.client import Client
from errbit_reporter.client import Notice


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
    def tearDown(self):
        TestHandler.request = None
        TestHandler.response = None

    def test_notify(self):
        response_filename = os.path.join(os.path.dirname(__file__), 'fixtures', 'response.xml')
        with open(response_filename) as f:
            body = f.read()
        TestHandler.response = FakeResponse(body)

        config = Configuration('apikey', 'http://localhost')
        client = Client(config)
        try:
            int('a')
        except:
            expected_body = Notice.from_exception(config, sys.exc_info()).serialize()
            metadata = client.notify()
        self.assertEqual(TestHandler.request.get_full_url(), "http://localhost/notifier_api/v2/notices/")
        self.assertEqual(TestHandler.request.get_method(), "POST")
        self.assertEqual(TestHandler.request.data, expected_body)
        self.assertEqual(metadata.id, '87186dda0c1d88569a171698')
        self.assertEqual(metadata.err_id, '7eafc85735047f2e5c9272b7')
        self.assertEqual(metadata.problem_id, '4886aba098109edbeb67a7f0')
