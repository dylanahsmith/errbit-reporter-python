from six.moves import urllib

from errbit_reporter.notice import Notice, Metadata


class Client(object):

    def __init__(self, config):
        self.config = config

    def notify(self, exc_info=None, request_url=None, component=None,
               action=None, params={}, session={}, cgi_data={}, timeout=None):
        notice = Notice.from_exception(self.config, exc_info)
        notice.request_url = request_url
        notice.component = component
        notice.action = action
        notice.params = params
        notice.session = session
        notice.cgi_data = cgi_data
        return self.send_notice(notice, timeout=timeout)

    def send_notice(self, notice, timeout=None):
        url = urllib.parse.urljoin(self.config.errbit_url, "/notifier_api/v2/notices/")
        request = urllib.request.Request(url, notice.serialize())
        request.add_header('Content-Type', 'text/xml')
        request.add_header('Accept', 'text/xml, application/xml')
        response = urllib.request.urlopen(request, timeout=timeout)
        return Metadata.from_notice_xml(response.read())
