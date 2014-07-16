from contextlib import contextmanager

from six.moves import urllib

from errbit_reporter import Notice, NoticeMetadata


class Client(object):
    """Errbit client used to send the notice to errbit

    Parameters:
        config : errbit_reporter.Configuration
            Used to build the notice and its errbit_url is used to send the notice.
    """

    def __init__(self, config):
        self.config = config

    @contextmanager
    def notify_on_exception(self, request_url=None, component=None, action=None,
                            params={}, session={}, cgi_data={}, timeout=None):
        """Context manager that notifies errbit of any exceptions.

        The exception will be re-raised after notifying errbit.

        Parameters:
            request_url : str, optional
                The url field that will be shown by errbit on the error page
            component : str, optional
                The 1st part of the *where* field on the error page in errbit
            action : str, optional
                The 2nd part of the *where* field on the error page in errbit
            params : dict of str, {str, list, dict} pairs, optional
                The data shown in the Parameters tab with the error in errbit.
            session : dict of str, {str, list, dict} pairs, optional
                The data shown in the Session tab with the error in errbit.
            cgi_data : dict of str, {str, list, dict} pairs, optional
                The data shown in the Environment tab with the error in errbit.
            timeout : int, optional
                The timeout in seconds for the request to errbit (the default is no
                timeout)
        """
        try:
            yield
        except Exception:
            notice = Notice.from_exception(self.config)
            notice.request_url = request_url
            notice.component = component
            notice.action = action
            notice.params = params
            notice.session = session
            notice.cgi_data = cgi_data
            self.send_notice(notice, timeout=timeout)
            raise

    def notify(self, exc_info=None, request_url=None, component=None,
               action=None, params={}, session={}, cgi_data={}, timeout=None):
        """Notify errbit of an exception

        Parameters:
            exc_info : (type, Exception, traceback), optional
                Information from sys.exc_info() to notify errbit about (the default
                is the exception currently being handled)
            request_url : str, optional
                The url field that will be shown by errbit on the error page
            component : str, optional
                The 1st part of the *where* field on the error page in errbit
            action : str, optional
                The 2nd part of the *where* field on the error page in errbit
            params : dict of str, {str, list, dict} pairs, optional
                The data shown in the Parameters tab with the error in errbit.
            session : dict of str, {str, list, dict} pairs, optional
                The data shown in the Session tab with the error in errbit.
            cgi_data : dict of str, {str, list, dict} pairs, optional
                The data shown in the Environment tab with the error in errbit.
            timeout : int, optional
                The timeout in seconds for the request to errbit (the default is no
                timeout)

        Returns:
            errbit_reporter.NoticeMetadata
                Identifiers to find the notice, error or problem in errbit
        """
        notice = Notice.from_exception(self.config, exc_info)
        notice.request_url = request_url
        notice.component = component
        notice.action = action
        notice.params = params
        notice.session = session
        notice.cgi_data = cgi_data
        return self.send_notice(notice, timeout=timeout)

    def send_notice(self, notice, timeout=None):
        """Send a Notice to errbit for an error

        Parameters:
            notice : errbit_reporter.Notice
                The notice to send to errbit that describes the error
            timeout : int, optional
                The timeout in seconds for the request to errbit (the default is no
                timeout)
        """
        if not self.config.errbit_url:
            return None
        url = urllib.parse.urljoin(self.config.errbit_url, "/notifier_api/v2/notices/")
        request = urllib.request.Request(url, notice.serialize())
        request.add_header('Content-Type', 'text/xml')
        request.add_header('Accept', 'text/xml, application/xml')
        response = urllib.request.urlopen(request, timeout=timeout)
        return NoticeMetadata.from_notice_xml(self.config, response.read())
