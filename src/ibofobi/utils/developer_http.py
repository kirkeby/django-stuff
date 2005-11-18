#!/usr/bin/env python

# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

import os
import sys
import getopt
import socket
import warnings
import errno
from cStringIO import StringIO
import logging
import traceback

from django.core.handlers.wsgi import WSGIHandler

MAX_HEAD_LENGTH = 1024
MAX_CONTENT_LENGTH = 1024 * 1024

log = logging.getLogger()

class Response:
    def __init__(self, transport):
        self.transport = transport
        self.decapitated = 0
        self.started = 0
        self.status = None
        self.headers = None

    def start_response(self, status, headers, exc_info=None):
        assert len(status) > 4

        if exc_info:
            try:
                if self.decapitated:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None # avoid dangling circular ref
        elif self.started:
            raise AssertionError("start_response already called")

        self.started = 1
        self.status = status
        self.headers = headers

        return self.write

    def write(self, data):
        if not self.started:
            raise AssertionError('start_response not called')

        if not self.decapitated:
            self.decapitated = 1
            self.transport.write('HTTP/1.0 ' + self.status + '\r\n')
            for key, val in self.headers:
                self.transport.write(key + ': ' + val + '\r\n')
            self.transport.write('\r\n')

        self.transport.write(data)

    def send_error_page(self, status, why):
        if self.decapitated:
            return

        self.transport.write('HTTP/1.0 ' + status + '\r\n')
        self.transport.write('Content-Type: text/plain\r\n')
        self.transport.write('\r\n')
        self.transport.write(why)

class BadRequestError(Exception):
    pass

class BaseWSGIServer:
    def __init__(self, application=None):
        if application:
            self.application = application

    def __call__(self, transport):
        """BaseWSGIServer.__call__(transport)

        Called when a client connects."""

        try:
            response = Response(transport)
            try:
                self.__handle_request(transport, response)

            except BadRequestError, why:
                log.error('Bad Request: ' + why.args[0].rstrip('\r\n'))
                response.send_error_page('500 Bad Request', why)

            except:
                log.exception('Internal Server Error')
                response.send_error_page('500 Internal Server Error',
                                         'Internal Error\r\n')

        finally:
            transport.close()

    def __handle_request(self, transport, response):
        # read request-line (i.e. "GET /... HTTP/x.y")
        request = transport.readline().rstrip('\r\n')
        try:
            method, uri, protocol = request.split()
        except ValueError:
            raise BadRequestError, 'Bad Request: ' + request + '\r\n'
    
        # read HTTP headers
        hl = 0
        headers = []
        host = ''
        content_type = ''
        content_length = ''
        while 1:
            line = transport.readline().rstrip('\r\n')
            hl = hl + len(line) + 2
            if hl > MAX_HEAD_LENGTH:
                raise BadRequestError, 'Headers too long.\r\n'
            if not line:
                break
            key, val = line.split(':', 1)
            key, val = key.rstrip(), val.lstrip()
            headers.append((key, val))

            key = key.lower()
            if key == 'content-type':
                content_type = val
            elif key == 'content-length':
                content_length = val

        # read HTTP content
        try:
            cl = int(content_length)
        except ValueError:
            cl = None
        if cl is None:
            content = ''
            transport.shutdown(0)
        elif cl > MAX_CONTENT_LENGTH:
            raise BadRequestError, 'Content too long.\r\n'
        else:
            content = transport.read(cl)
            transport.shutdown(0)

        # find WSGI application
        pieces = uri.split('?', 1)
        if len(pieces) == 1:
            path_info, query_string = uri, ''
        else:
            path_info, query_string = pieces
        app, script_name, path_info = self.find_application(host, path_info)

        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO(content),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': 1,
            'wsgi.multiprocess': 0,
            'wsgi.run_once': 0,

            'REQUEST_METHOD': method.upper(),
            'REMOTE_ADDR': transport.there[0],
            'SCRIPT_NAME': script_name,
            'PATH_INFO': path_info,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': content_length,
            'SERVER_NAME': transport.here[0],
            'SERVER_PORT': str(transport.here[1]),
            'SERVER_PROTOCOL': protocol,
        }
        for key, val in headers:
            if key.lower() in ('Content-Type', 'Content-Length'):
                continue
            env['HTTP_' + key.upper().replace('-', '_')] = val

        try:
            result = app(env, response.start_response)
        except:
            exc_info = sys.exc_info()
            log.exception(exc_info)

            transport.write('HTTP/1.0 500 Internal Server Error\r\n')
            transport.write('Content-Type: text/plain\r\n\r\n')
            traceback.print_exception(exc_info[0], exc_info[1], exc_info[2],
                                      file=transport)
            transport.close()
            return

        try:
            for data in result:
                if data: # don't send headers until body appears
                    response.write(data)
            if not response.decapitated:
                response.write('')
        finally:
            if hasattr(result, 'close'):
                result.close()

    def find_application(self, host, path_info):
        return self.application, '', path_info

class SocketTransport:
    """A helper-class wrapping sockets in a transport-interface."""
    __file_methods__ = ['read', 'readline', 'readlines',
                        'write', 'writelines']
    __socket_methods__ = ['shutdown']
    def __init__(self, sock):
        self.sock = sock
        self.file = file = os.fdopen(sock.fileno(), 'r+')
        self.closed = False
        for o, m in ((file, self.__file_methods__),
                     (sock, self.__socket_methods__)):
            for n in m:
                setattr(self, n, getattr(o, n))

        self.here = sock.getsockname()
        self.there = sock.getpeername()

    def close(self):
        if self.closed:
            return
        self.file.flush()
        self.file.close()
        self.sock.close()
        self.closed = True

def main(argv):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter())
    log.addHandler(handler)

    server = BaseWSGIServer(WSGIHandler())

    interface = ''
    port = 8080
    socket_fd = None
    max_requests = 1
    settings = None

    opts, args = getopt.getopt(argv[1:], '', ('socket-fd=', 'port=', 'bind=',
                                              'max-requests=', 'settings='))
    for k, v in opts:
        if k == '--socket-fd':
            socket_fd = int(v)
        elif k == '--port':
            port = int(v)
        elif k == '--bind':
            interface = v
        elif k == '--max-requests':
            max_requests = int(v)
        elif k == '--settings':
            settings = v
        else:
            raise 'Bad, bad getop! %r' % k

    if not settings is None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings

    from django.conf import settings
    settings.DEBUG = True
            
    if socket_fd is None:
        log.info('Creating listener socket for %s:%d' % (interface, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((interface, port))
        sock.listen(1)

    else:
        log.info('Reusing listener socket %d' % socket_fd)
        sock = socket.fromfd(socket_fd, socket.AF_INET, socket.SOCK_STREAM)

    try:
        for i in range(max_requests):
            s, o = sock.accept()
            try:
                server(SocketTransport(s))
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(exc_info[0], exc_info[1], exc_info[2])

        # close all open file-descriptors, which are not std{in,out,err} or
        # our listening socket,
        for fd in range(3, os.sysconf('SC_OPEN_MAX')):
            if fd == sock.fileno():
                continue
            try:
                os.close(fd)
            except OSError, (eno, _):
                if not eno == errno.EBADF:
                    warnings.warn('errno %d closing fd %d' % (eno, fd))

        print "Re-exec'ing myself"
        os.execv(argv[0], [argv[0], '--socket-fd', str(sock.fileno()),
                                    '--max-requests', str(max_requests)])

    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
