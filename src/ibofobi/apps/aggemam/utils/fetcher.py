import urlparse
import httplib

AGGEMAM_MAX_REDIRECT_DEPTH = 3

class Fetcher:
    def __init__(self, url):
        self.url = url

        self.request_headers = {
            'User-Agent': 'Aggemam (+http://ibofobi.dk/stuff/aggemam/)',
        }
        self.status = self.reason = self.headers = self.body = None
    
    def fetch(self):
        r, b = self.__fetch(self.url, 0)

        self.status = r.status
        self.reason = r.reason
        self.headers = ''.join(r.msg.headers)
        self.parsed = r.msg
        self.body = b

    def __fetch(self, url, redirect_depth):
        if redirect_depth == AGGEMAM_MAX_REDIRECT_DEPTH:
            raise AssertionError, 'maximum redirect depth hit'

        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)

        if not scheme == 'http':
            raise AssertionError, 'unknown scheme: %s' % url

        c = httplib.HTTPConnection(netloc)
        c.request('GET', path + '?' + query, headers=self.request_headers)
        r = c.getresponse()
        body = r.read()
        c.close()

        if r.status == 302:
            # Handle "302 Found" (i.e. temporarily moved),
            url = r.msg['location']
            return self.__fetch(url, redirect_depth + 1)

        else:
            return r, body
