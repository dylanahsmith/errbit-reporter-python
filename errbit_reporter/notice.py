import sys
import types
import traceback
import re
from xml.etree import cElementTree as ET

import six


class Notice(object):
    INVALID_TAG_CHARS = re.compile("[^a-zA-Z0-9_-]")

    def __init__(self, config, error_class, error_message, backtrace=None):
        self.config = config

        if isinstance(error_class, type):
            error_class = error_class.__name__
        self.error_class = error_class
        if isinstance(error_message, Exception):
            error_message = error_class + ": " + str(error_message)
        self.error_message = error_message
        if isinstance(backtrace, types.TracebackType):
            backtrace = traceback.extract_tb(backtrace)
        elif backtrace is None:
            backtrace = sys.extract_stack()
        self.backtrace = backtrace

        self.request_url = None
        self.component = None
        self.action = None
        self.params = {}
        self.session = {}
        self.cgi_data = {}

    @classmethod
    def from_exception(cls, config, exc_info=None):
        if exc_info is None:
            exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        return cls(config, *exc_info)

    def serialize(self):
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


class Metadata(object):
    def __init__(self, id, err_id, problem_id, app_id, created_at, updated_at):
        self.id = id
        self.err_id = err_id
        self.problem_id = problem_id
        self.app_id = app_id
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_notice_xml(cls, body):
        tree = ET.fromstring(body)

        id = tree.findtext('./_id')
        err_id = tree.findtext('./err-id')
        problem_id = tree.findtext('./problem-id')
        app_id = tree.findtext('./app-id')
        created_at = tree.findtext('./created-at')
        updated_at = tree.findtext('./updated-at')

        return cls(id, err_id, problem_id, app_id, created_at, updated_at)
