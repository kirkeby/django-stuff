
from cgi import parse_qs
from urlparse import urlsplit
import httplib
import re
import base64

from ibofobi.apps.aurora.utils.BeautifulSoup import BeautifulSoup

class TvTorrentsSession:
    def __init__(self):
        self.conn = httplib.HTTPConnection('www.tvtorrents.com')
        self.session_cookie = None
        self.user_agent = 'AuroraFeeder/0.1 +http://code.ibofobi.dk/public/wiki/AuroraFeeder'

    def login(self, username, password):
        # First, get a session
        self.conn.putrequest('GET', '/')
        self.conn.putheader('User-Agent', self.user_agent)
        self.conn.endheaders()
        
        resp = self.conn.getresponse()
        soup = BeautifulSoup(resp.read())
        if soup.h1.string == 'error encountered':
            raise AssertionError

        self.session_cookie = resp.getheader('set-cookie').split(';', 1)[0]
        
        # Now login,
        login_form = 'username=%s&password=%s&posted=true' % (username, password)
        self.conn.putrequest('POST', '/login.do')
        self.conn.putheader('User-Agent', self.user_agent)
        self.conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
        self.conn.putheader('Content-Length', str(len(login_form)))
        self.conn.putheader('Cookie', self.session_cookie)
        self.conn.endheaders()
        self.conn.send(login_form)

        resp = self.conn.getresponse()
        soup = BeautifulSoup(resp.read())
        if soup.h1.string == 'error encountered':
            raise AssertionError
        if soup.form.get('name', None) == 'loginForm':
            raise AssertionError

    def get_page(self, url, soup=True):
        assert self.session_cookie

        self.conn.putrequest('GET', url)
        self.conn.putheader('User-Agent', self.user_agent)
        self.conn.putheader('Cookie', self.session_cookie)
        self.conn.endheaders()

        resp = self.conn.getresponse()
        if soup:
            soup = BeautifulSoup(resp.read())
            if soup.h1.string == 'error encountered':
                raise AssertionError

            return soup

        else:
            return resp.read()

def main(seen_path, login, password, callback):
    # Load list of seen torrents
    seen = {}
    seen_file = open(seen_path)
    for infohash in seen_file:
        seen[infohash.strip()] = True

    seen_file = open(seen_path, 'a')
    
    # Connect to tvtorrents
    tvtorrents = TvTorrentsSession()
    tvtorrents.login(login, password)

    # Get list of favourite shows
    soup = tvtorrents.get_page('/loggedin/my/fav_shows.do')
    shows = soup('a', { 'href': re.compile(r'^/loggedin/show.do\?') })

    for show in shows:
        # Naviagate to the next 'a' tag, should be the current episode
        tag = show.next
        while not getattr(tag, 'name', None) == 'a':
            tag = tag.next

        # Get torrent infohash
        qs = urlsplit(tag['href'])[3]
        qs = parse_qs(qs)
        infohash, = qs['info_hash']

        # Skip torrent if we've already seen it
        if seen.has_key(infohash):
            continue
        
        # Download torrent
        try:
            torrent_data = tvtorrents.get_page('/loggedin/TorrentLoaderServlet?info_hash=%s' % infohash, soup=False)
        except:
            print 'Failed getting "%s"' % infohash
            continue

        # Do the thang, dawg!
        callback(show, tag, torrent_data)

        # Mental note to self
        seen[infohash] = True
        seen_file.write(infohash + '\n')
