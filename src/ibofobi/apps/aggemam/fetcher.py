import urlparse
import httplib

class Fetcher:
    def __init__(self, url):
        self.url = url

        self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = \
            urlparse.urlparse(self.url)

        self.request_headers = {
            #'User-Agent': 'Aggemam
        }
        self.status = self.reason = self.headers = self.body = None
    
    def fetch(self):
        c = httplib.HTTPConnection(self.netloc)
        c.request('GET', self.path + '?' + self.query,
                  headers=self.request_headers)
        r = c.getresponse()
        self.status = r.status
        self.reason = r.reason
        self.headers = ''.join(r.msg.headers)
        self.parsed = r.msg
        self.body = r.read()
        c.close()
