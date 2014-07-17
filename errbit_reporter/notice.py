import sys
import types
import traceback
import re
from xml.etree import cElementTree as ET

import six
from six.moves import urllib


class Notice(object):
    """The description of an exception that can be sent to errbit"""

    INVALID_TAG_CHARS = re.compile("[^a-zA-Z0-9_-]")

    def __init__(self, config, error_class, error_message, backtrace=None):
        self.config = config

        self.error_class = error_class
        self.error_message = error_message
        if backtrace is None:
            backtrace = traceback.extract_stack()
        self.backtrace = backtrace
        self.request_url = None
        self.component = None
        self.action = None
        self.params = {}
        self.session = {}
        self.cgi_data = {}

    @property
    def error_class(self):
        return self._error_class

    @error_class.setter
    def error_class(self, value):
        if isinstance(value, type):
            value = value.__name__
        self._error_class = value

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        if isinstance(value, Exception):
            value = value.__class__.__name__ + ": " + str(value)
        self._error_message = value

    @property
    def backtrace(self):
        return self._backtrace

    @backtrace.setter
    def backtrace(self, value):
        if isinstance(value, types.TracebackType):
            value = traceback.extract_tb(value)
        elif value is None:
            value = []
        self._backtrace = value

    @classmethod
    def from_exception(cls, config, exc_info=None):
        "Creates a notice from an exception"
        if exc_info is None:
            exc_info = sys.exc_info()
            if exc_info[1] is None:
                raise ValueError("exc_info is required outside of an exception handler")
        exc_type, exc_value, exc_tb = exc_info
        return cls(config, *exc_info)

    def serialize(self):
        "Serialize the notice to xml which errbit accepts for notice creation"
        root = ET.Element('notice', version="2.4")

        ET.SubElement(root, 'api-key').text = self.config.api_key

        notifier = ET.SubElement(root, 'notifier')
        ET.SubElement(notifier, 'name').text = self.config.notifier_name
        ET.SubElement(notifier, 'version').text = self.config.notifier_version
        ET.SubElement(notifier, 'url').text = self.config.notifier_url

        error = ET.SubElement(root, 'error')
        ET.SubElement(error, 'class').text = self.error_class
        ET.SubElement(error, 'message').text = self.error_message
        backtrace = ET.SubElement(error, 'backtrace')
        for filename, line_number, function_name, text in reversed(self.backtrace):
            ET.SubElement(
                backtrace, 'line', number=str(line_number), file=filename, method=function_name)

        request = ET.SubElement(root, 'request')
        ET.SubElement(request, 'url').text = self.request_url
        ET.SubElement(request, 'component').text = self.component
        ET.SubElement(request, 'action').text = self.action
        self._add_xml_dict(ET.SubElement(request, 'params'), self.params)
        self._add_xml_dict(ET.SubElement(request, 'session'), self.session)
        self._add_xml_dict(ET.SubElement(request, 'cgi-data'), self.cgi_data)

        server_env = ET.SubElement(root, 'server-environment')
        ET.SubElement(
            server_env, 'project-root').text = self.config.project_root
        ET.SubElement(
            server_env, 'environment-name').text = self.config.environment_name
        ET.SubElement(server_env, 'hostname').text = self.config.server_name

        buffer = six.BytesIO()
        ET.ElementTree(root).write(
            buffer, encoding='utf-8', xml_declaration=True)
        xml_string = buffer.getvalue()
        buffer.close()
        return xml_string

    def _sanitize_tag(self, tag):
        "Sanitize tag string to avoid xml injection from user supplied params"
        if not tag:
            tag = "_"
        tag = self.INVALID_TAG_CHARS.sub('-', tag)
        if tag[0] == "-":
            tag[0] = "_"
        return tag

    def _add_xml_dict(self, parent, args):
        for name, value in six.iteritems(args):
            child = ET.SubElement(parent, name)
            self._add_xml_value(child, value)

    def _add_xml_value(self, parent, value):
        if isinstance(value, dict):
            self._add_xml_dict(parent, value)
        elif isinstance(value, list):
            for item in value:
                child = ET.SubElement(parent, 'item')
                self._add_xml_value(child, item)
        else:
            parent.text = str(value)


class NoticeMetadata(object):
    """Metadata that returned by errbit that identifies a notice

    Can be used to get the url to see the error page for the notice in errbit.
    """

    def __init__(self, config, id, err_id, problem_id, app_id, created_at, updated_at):
        self.config = config
        self.id = id
        self.err_id = err_id
        self.problem_id = problem_id
        self.app_id = app_id
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_notice_xml(cls, config, body):
        "Extracts the metadata from the response body of a notify request"
        tree = ET.fromstring(body)

        id = tree.findtext('./_id')
        err_id = tree.findtext('./err-id')
        problem_id = tree.findtext('./problem-id')
        app_id = tree.findtext('./app-id')
        created_at = tree.findtext('./created-at')
        updated_at = tree.findtext('./updated-at')

        return cls(config, id, err_id, problem_id, app_id, created_at, updated_at)

    @property
    def url(self):
        "Returns the url that shows the notice on errbit"
        path = "/apps/%s/errs/%s/notices/%s" % (self.app_id, self.problem_id, self.id)
        return urllib.parse.urljoin(self.config.errbit_url, path)
