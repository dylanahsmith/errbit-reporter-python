import sys
import os.path
import traceback
import unittest
from xml.etree import cElementTree as ET

from errbit_reporter import Configuration, Notice, NoticeMetadata


class NoticeTest(unittest.TestCase):

    def setUp(self):
        self.config = Configuration('apikey', 'http://localhost:3000')

    def test_serialize(self):
        backtrace = [
            ('foo/main.py', 11, '<module>', 'foo()'),
            ('foo/main.py', 5, 'foo', 'bar([])'),
            ('foo/main.py', 8, 'bar', 'a[-1]')
        ]
        notice = Notice(self.config, 'IndexError', 'list index out of range', backtrace)
        xml = notice.serialize()
        tree = ET.fromstring(xml)

        self.assertEqual(tree.findtext('./api-key'), 'apikey')
        self.assertEqual(tree.findtext('./error/class'), 'IndexError')
        self.assertEqual(tree.findtext('./error/message'), 'list index out of range')

        bt_elements = tree.findall('./error/backtrace/line')
        expect = list(reversed([line[:3] for line in backtrace]))
        got = [(e.attrib['file'], int(e.attrib['number']), e.attrib['method']) for e in bt_elements]
        self.assertEqual(got, expect)

    def test_from_exception(self):
        try:
            raise ValueError('oops')
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            notice = Notice.from_exception(self.config)

        self.assertEqual(notice.error_class, 'ValueError')
        self.assertEqual(notice.error_message, 'ValueError: oops')
        self.assertEqual(notice.backtrace, traceback.extract_tb(exc_tb))

    def test_params(self):
        notice = Notice(self.config, 'IndexError', 'list index out of range', [])
        notice.params['id'] = 1
        notice.params['attributes'] = {
            'refs': [2, 3]
        }
        xml = notice.serialize()
        tree = ET.fromstring(xml)

        self.assertEqual(tree.findtext('./request/params/id'), '1')
        refs = [e.text for e in tree.findall('./request/params/attributes/refs/item')]
        self.assertEqual(refs, ['2', '3'])

    def test_metadata_from_response(self):
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'response.xml')
        with open(fixture_path, 'rb') as f:
            notice_xml = f.read()
        metadata = NoticeMetadata.from_notice_xml(notice_xml)
        self.assertEqual(metadata.id, '87186dda0c1d88569a171698')
        self.assertEqual(metadata.app_id, 'ff283e00de6339078233c722')
        self.assertEqual(metadata.err_id, '7eafc85735047f2e5c9272b7')
        self.assertEqual(metadata.problem_id, '4886aba098109edbeb67a7f0')
        self.assertEqual(metadata.created_at, '2014-07-14T10:50:02-04:00')
        self.assertEqual(metadata.updated_at, '2014-07-14T10:50:02-04:00')
