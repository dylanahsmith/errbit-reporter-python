Python Errbit Reporter
======================

A client for reporting exceptions to errbit.

Installation
------------

.. code:: shell

    pip install errbit_reporter

Usage
-----

.. code:: python

    import errbit_reporter as errbit

    config = errbit.Configuration(
        api_key='491b8cbb777b051df1406ae0bcdbee2c',
        errbit_url='http://errbit.yourserver.com')

    client = errbit.Client(config)
    with client.notify_on_exception():
        your_code_here()

To avoid sending exceptions in development, just use `None`
for the errbit_url. For example:

.. code:: python

    config = errbit.Configuration(
        api_key='491b8cbb777b051df1406ae0bcdbee2c',
        errbit_url=None,
        environment_name='development')

Additional context can be provided for the error.  For example:

.. code:: python

    context = {
        'request_url': 'http://example.com/account/signup',
        'component': 'AccountController',
        'action': 'signup',
        'params': {
            'user': {
                'name': 'dylan'
            }
        },
        'cgi_data': {
            'REQUEST_METHOD': 'POST',
            'HTTP_USER_AGENT': 'curl'
        },
        'session' {
            'session_id': '6df95c0296cee016fb672af9310667e24dca066909a723dd6439369bb82911f3'
        }
    }
    with client.notify_on_exception(**context):
        your_code_here()

A notice can also be sent without a context manager to get
notice metadata which can be used to log the errbit notice url.

.. code:: python

    try:
        your_code_here()
    except:
        notice_metadata = client.notify()
        print(notice_metadata.url)

By default the exception information is taken from sys.exc_info(),
but exc_info can also be passed as the first parameter, and additional
context can be provided using the same keyword arguments as
notify_on_exception.

In a distributed system (e.g. [Spark](https://spark.apache.org/))
it is useful to be able to specify the backtrace manually. For
example, this the backtrace could consist of local and remote
processes stack trace, even if the remote processes is written in
another language.

.. code:: python

    exc_type, exc_value, exc_traceback = sys.exc_info()
    backtrace = traceback.extract_tb(exc_traceback)
    notice = errbit.Notice(config, exc_type.__name__, str(exc_value), backtrace)
    client.send_notice(notice)

Test Suite
----------

.. code:: shell

    make test

Copyright
---------

Copyright (c) 2014 "Shopify Inc.". See LICENSE for details.
