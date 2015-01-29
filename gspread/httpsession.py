# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

try:
#    import httplib as client
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:
#    from http import client
    from urllib.parse import urlparse
    from urllib.parse import urlencode

from requests import Request, Session, request
from io import StringIO

try:
    unicode
except NameError:
    basestring = unicode = str


class HTTPError(Exception):
    def __init__(self, response):
        self.code = response.status
        self.response = response

    def read(self):
        return self.response.read()


class HTTPSession(object):
    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
       :param timeout: Timeout for http requested (default (10,60)
                       10 seconds for connection, 60 seconds for read)
    """
    def __init__(self, headers=None, timeout=10):
        self.headers = headers or {}
        self.connections = {}
        self.timeout = timeout

    def request(self, method, url, data=None, headers=None):
        if data and not isinstance(data, basestring):
            data = urlencode(data)

        if data is not None:
            data = data.encode()

        # If we have data and Content-Type is not set, set it...
        if data and not headers.get('Content-Type', None):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # If connection for this scheme+location is not established, establish it.
        uri = urlparse(url)
        if not self.connections.get(uri.scheme+uri.netloc):
            session = Session()
            session.headers = self.headers.copy()
            self.connections[uri.scheme+uri.netloc] = session

        session = self.connections[uri.scheme+uri.netloc]
        response = session.request(method, url, data=data,
                                   headers=headers,
                                   timeout=self.timeout)

        if response.status_code > 399:
            raise HTTPError(response)
        return response.text

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def post(self, url, data=None, headers={}):
        return self.request('POST', url, data=data, headers=headers)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def add_header(self, name, value):
        self.headers[name] = value
