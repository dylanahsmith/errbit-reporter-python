import os
import socket


class Configuration(object):
    """Parameters that are used across clients and error notices

    Parameters:
        api_key : str
            errbit provided to the app to associate errors with it
        errbit_url : str
            protocol and host of the errbit server (e.g. "https://api.airbrake.io")
        project_root : str, optional
            Directory of the project's source code which is replaced by
            [PROJECT_ROOT] in the backtrace and linked to line on github.
            (the defaults is the current working directory)
        environment_name : str
            Environment field on the error's page (the default is 'production')
        server_name : str
            App Server field on error's page (the default is the server's hostname)
    """

    def __init__(self, api_key, errbit_url, project_root=None, environment_name='production', server_name=None):
        self.api_key = api_key
        self.errbit_url = errbit_url

        self.notifier_name = 'Python Errbit Reporter'
        self.notifier_version = '0.0.1'
        self.notifier_url = 'https://github.com/dylanahsmith/python-errbit-reporter'

        self.project_root = project_root or os.getcwd()
        if not self.project_root.endswith('/'):
            self.project_root += '/'
        self.environment_name = environment_name
        self.server_name = server_name or socket.gethostname()
