# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core.handlers.wsgi import WSGIHandler
from BeautifulSoup import BeautifulSoup

# Browser for ...
class Result:
    def start_response(self, status, headers):
        self.status = status
        self.headers = headers
        return self.write
    def write(self, *args):
        raise NotImplementedError

class Browser:
    def __init__(self, app):
        self.handler = WSGIHandler()
        self.result = None
    
    def go(self, url, code=200):
        environ = {
            'PATH_INFO': url,
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
        }

        self.result = Result()
        pieces = self.handler(environ, self.result.start_response)
        self.result.body = ''.join(pieces)
        self.soup = BeautifulSoup(self.result.body)

        if not self.result.status.startswith('%d ' % code):
            raise AssertionError, self.result.status

    def content_type(self):
        """Return Content-Type header of last document fetched."""
        for k, v in self.result.headers:
            if k.lower() == 'content-type':
                return v

