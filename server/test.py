#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014-2015 jeffZhuo
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement
from __future__ import nested_scopes
from __future__ import generators

import time
import socket
import atexit
import sys

try:
    import cStringIO as StringIO
except (Exception, ):
    import StringIO

from mimetools import Message
from traceback import print_exception
from server.header import ResponseHeaders
from server.header import format_date_time


# class RequestHadler(object):
#
#     http_version = "1.1"
#     server_software = "Test Server"
#
#     error_status = "500 Internal Server Error"
#     error_headers = [('Content-Type', 'text/plain')]
#     error_body = "A server error occurred.  Please contact the administrator."
#
#     def __init__(self, server, rfile, wfile, addr):
#
#         self.rfile = rfile
#         self.wfile = wfile
#         self.stderr = sys.stderr
#
#         self.addr = addr
#         self.server = server
#
#         self.application = server.application
#
#         self.environ = None
#
#         self.__commond = None
#         self.__path = None
#         self.__query = None
#         self.__version = None
#         self.__header = []
#         self.__body = None
#
#         self.request_startline = None
#
#         # For write() and startResponse()
#         self.result = None
#         self.header_sent = False
#         self.response_status = None
#         self.response_header = None
#         self.bytes_sent = 0
#
#     def handle_one_request(self):
#         """ Main function of the handler.
#         parse_request -> run() -> close()
#         :return: None
#         """
#         self.request_startline = self.rfile.readline(65537)
#         self.parse_request()
#         self.run()
#         self.rfile.close()
#         self.wfile.close()
#
#     def parse_request(self):
#         """ Parse the request content """
#         startline = self.request_startline.replace('\r\n', '\n').replace('\r', '\n')
#         # Parse the first line of request
#         self.__commond, self.__path, self.__query, self.__version = self.__parse_startline(startline)
#         # Get the header from request
#         self.__header = Message(self.rfile)
#
#     @staticmethod
#     def __parse_startline(startline):
#         """ Parse the first line of request
#         To get commond(e.g: GET, POST....),
#         path,
#         query(e.g:?user=user)
#         version(The version of HTTP request, e.g:HTTP/1.1)
#         """
#         commond, path, version = startline.split()
#         if '?' in path:
#             path, query = path.split("?", 1)
#         else:
#             path, query = path, ""
#
#         return commond, path, query, version
#
#     def run(self):
#         try:
#             environ = self.getenv()
#             self.result = self.application(environ, self.start_response)
#             self.finish_response()
#         except:
#             try:
#                 self.handle_error()
#             except:
#                 self.close()
#
#     def set_cgi_environ(self, environ):
#         """ Setting the cgi environ """
#         # Request http version
#         environ['SERVER_PROTOCOL'] = self.__version
#         environ['REQUEST_METHOD'] = self.__commond
#         environ['PATH_INFO'] = self.__path
#         environ['QUERY_STRING'] = self.__query
#
#         if self.__header.typeheader is None:
#             environ['CONTENT_TYPE'] = self.__header.type
#         else:
#             environ['CONTENT_TYPE'] = self.__header.typeheader
#
#         length = self.__header.getheader('content_length')
#         if length:
#             environ["CONTENT_LENGTH"] = length
#
#         for h in self.__header.headers:
#             k, v = h.split(":", 1)
#             k = k.replace("-", "_").upper();
#             v = v.strip()
#             if k in environ:
#                 continue
#             if "HTTP_" + k in environ:
#                 environ["HTTP_" + k] += "," + v
#             else:
#                 environ["HTTP_" + k] = v
#
#     def getenv(self):
#         """ Get the environ """
#         environ = self.server.base_environ.copy()
#         environ["wsgi.version"] = (1, 0)
#         environ["wsgi.input"] = self.rfile
#         environ["wsgi.error"] = self.wfile
#         environ["wsgi.multithread"] = False
#         environ["wsgi.multiprocess"] = False
#         environ["wsgi.run_once"] = False
#
#         if environ.get("HTTPS", "off") in ("on", "1"):
#             environ["wsgi.url_scheme"] = "https"
#         else:
#             environ["wsgi.url_scheme"] = "http"
#
#         if self.server_software:
#             environ['SERVER_SOFTWARE'] = self.server_software
#
#         # CGI environ
#         self.set_cgi_environ(environ)
#
#         self.environ = environ
#         return environ
#
#     def finish_response(self):
#         """ Send the iterable data, then close self and the iterable data
#         """
#         try:
#             for data in self.result:
#                 self.write(data)
#             self.finish_content()
#         finally:
#             self.close()
#
#     def close(self):
#         """ Close the the iterable """
#         if hasattr(self.result, "close"):
#             self.result.close()
#
#     def finish_content(self):
#         """Ensure headers and content have both been sent"""
#         if not self.header_sent:
#             # Only zero Content-Length if not set by the application (so
#             # that HEAD requests can be satisfied properly, see #3839)
#             if self.response_header.get('Content-Length') is None:
#                 self.response_header.add_header('Content-Length', 0)
#             self.send_headers()
#         else:
#             pass # XXX check if content-length was too short?
#
#     def write(self, data):
#         if not self.response_status:
#             raise AssertionError("write() before start_response()")
#         if not self.header_sent:
#             self.bytes_sent = len(data)
#             self.send_headers()
#         else:
#             self.bytes_sent += len(data)
#
#         self._write(data)
#         self._flush()
#
#     def send_headers(self):
#         """ Send response header to client """
#         self.header_sent = True
#         self.setup_header()
#
#         self.send_preamble()
#         self._write(self.response_header)
#
#     def setup_header(self):
#         """ Make necessary header changes """
#         if "Content-Length" not in self.__header:
#             self.set_content_length()
#
#     def set_content_length(self):
#         """ Get the Content-Length if possible """
#         if 'Content-Length' not in self.response_header:
#             try:
#                 blocks = len(self.result)
#             except (TypeError,AttributeError,NotImplementedError):
#                 pass
#             else:
#                 if blocks == 1:
#                     self.response_header["Content-Length"] = str(self.bytes_sent)
#
#     def send_preamble(self):
#         """ Send version/status/date/server to client """
#         self._write('%s %s\r\n' % (self.version, self.response_status))
#         if "Date" not in self.response_header:
#             self._write("Date: %s\r\n" % format_date_time(time.time()))
#
#         if self.server_software and "Server" not in self.response_header:
#             self._write("Server: %s\r\n" % self.server_software)
#
#     def _write(self, data):
#         self.wfile.write(data)
#         self._write = self.wfile.write
#
#     def _flush(self):
#         self.wfile.flush()
#         self._flush = self.wfile.flush
#
#     def start_response(self, status, response_headers, excInfo=None):
#         if excInfo:
#             try:
#                 if self.header_sent:
#                     raise (excInfo[0], excInfo[1], excInfo[2])
#             finally:
#                 excInfo = None
#         elif self.header_sent:
#             raise AssertionError("Headers already set!")
#
#         self.response_status = status
#         self.response_header = ResponseHeaders(response_headers)
#         return self.write
#
#     def handle_error(self):
#         """ Send error output to client if possible """
#         self.log_exception(sys.exc_info())
#         if not self.header_sent:
#             self.result = self.error_output(self.environ, self.start_response)
#             self.finish_response()
#
#     def log_exception(self, exc_info):
#         """
#         Log the exc_info to server log by stderr
#         Can override this method to change the format
#         :param exc_info:
#         """
#         try:
#             print_exception(exc_info[0], exc_info[1], exc_info[2], None, self.stderr)
#         finally:
#             exc_info = None
#
#
#     def error_output(self, environ, start_response):
#         """
#
#         :param environ:
#         :param start_response:
#         :return error_body:
#         """
#         start_response(self.error_status, self.error_headers, sys.exc_info())
#         return [self.error_body]
#
#     def set_stderr(self, stderr):
#         """
#         Set the stderr for error out put
#         :param stderr:
#         :return:
#         """
#         self.stderr = stderr


class HTTPRequest(object):
    """
    The request form the socket, handle the request until the connections close.
    """
    MAX_URL_SIZE = 65537
    MAX_BODY_SIZE = 10485760  # 10MB = 1024 * 1024 * 10

    def __init__(self, server, rfile, wfile, addr):
        """
        :param server: the server obj
        :param rfile: the connection read file
        :param wfile: the connection write file
        :param addr: the remote address
        """
        self.server = server
        self.rfile = rfile
        self.wfile = wfile
        self.addr = addr

        self.commond = None
        self.path = None
        self.query = None
        self.version = None

        # request header
        self.headers = None

        # request body
        self.body = None

    def handle_one_request(self):
        self.parse_request()
        try:
            self.handle_request()
        except Exception as ex:
            # print log here
            print(ex)
            response = SimpleResponse(500, self.version, [('Content-Type', 'text/plain',), ], "")
            self.__write(response)
            self.__flush()
        finally:
            self.close()

    def parse_request(self):
        """
        Parse the http struct from 'rfile'
        """
        start_line = self.rfile.readline(HTTPRequest.MAX_URL_SIZE)
        start_line = start_line.replace('\r\n', '\n').replace('\r', '\n')
        self.commond, self.path, self.query, self.version = HTTPRequest.__parse_startline(start_line)

        self.headers = HTTPRequest.__parse_header(self.rfile)
        content_length = int(self.headers.get("Content-Length", 0))
        self.body = HTTPRequest.__parse_body(self.rfile, content_length)

    def handle_request(self):
        """
        The event processing here
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def __parse_startline(start_line):
        """
        Parse the start line, to get the commond, path, query, http version
        :param start_line:
        :return: (commond, path, query, http version)
        """
        print(start_line)
        commond, path, version = start_line.split(' ')
        if '?' in path:
            path, query = path.split('?', 1)
        else:
            path, query = path, ''

        return commond, path, query, version

    @staticmethod
    def __parse_header(rfile):
        """
        Parse the header after parse start line
        :param rfile: readable file(has been parse start line)
        :return: headers
        """
        headers = {}
        while True:
            one_line = rfile.readline()
            if not one_line:
                break
            if one_line == '\r\n' or one_line == '\n':
                break

            header, value = one_line.split(':', 1)
            headers[header] = value

        return headers

    @staticmethod
    def __parse_body(rfile, content_length=0):
        body = None
        #length = HTTPRequest.MAX_BODY_SIZE
        if content_length != 0 and content_length <= HTTPRequest.MAX_BODY_SIZE:
            # length = content_length
            body = rfile.read(content_length)

        return body

    def write(self, data):
        self.__write(data)

    def flush(self):
        self.__flush()

    def __write(self, data):
        self.wfile.write(data)
        self._write = self.wfile.write

    def __flush(self):
        self.wfile.flush()
        self._flush = self.wfile.flush

    def close(self):
        """
        Close this request
        :return:
        """
        self.rfile.close()
        self.wfile.close()


class WSGIRequest(HTTPRequest):

    def __init__(self, server, rfile, wfile, addr):
        super(WSGIRequest, self).__init__(server, rfile, wfile, addr)

        self.application = server.application
        self.environ = None

        self.stderr = None

        # For write() and startResponse()
        self.result = None
        self.header_sent = False
        self.response_status = None
        self.response_headers = None
        self.bytes_sent = 0

    def handle_request(self):
        """
        Call the function run() to invoke wsgi application
        :return:
        """
        self.run()

    def run(self):
        try:
            environ = self.getenv()
            self.result = self.application(environ, self.start_response)

            self.finish_response()
        except:
            try:
                self.handle_error()
            except:
                self.close()

    def getenv(self):
        """ Get the environ """
        environ = self.server.base_environ.copy()
        environ["wsgi.version"] = (1, 0)
        environ["wsgi.input"] = self.rfile
        environ["wsgi.error"] = self.wfile
        environ["wsgi.multithread"] = False
        environ["wsgi.multiprocess"] = False
        environ["wsgi.run_once"] = False

        if environ.get("HTTPS", "off") in ("on", "1"):
            environ["wsgi.url_scheme"] = "https"
        else:
            environ["wsgi.url_scheme"] = "http"

        if self.server.server_software:
            environ['SERVER_SOFTWARE'] = self.server.server_software

        # CGI environ
        self.set_cgi_environ(environ)

        self.environ = environ
        return environ

    def set_cgi_environ(self, environ):
        """ Setting the cgi environ """
        # Request http version
        environ['SERVER_PROTOCOL'] = self.version
        environ['REQUEST_METHOD'] = self.commond
        environ['PATH_INFO'] = self.path
        environ['QUERY_STRING'] = self.query

        environ['CONTENT_TYPE'] = self.headers.get('Content-Type', 'text/plain')

        length = self.headers.get('Content-Length')
        if length:
            environ["CONTENT_LENGTH"] = length

        for k, v in self.headers.items():
            k = k.replace('-', '_').upper()
            v = v.strip()

            if k in environ:
                continue
            if 'HTTP_' + k in environ:
                environ['HTTP_' + k] += ',' + v
            else:
                environ['HTTP_' + k] = v

    def start_response(self, status, response_headers, excInfo=None):
        if excInfo:
            try:
                if self.header_sent:
                    raise (excInfo[0], excInfo[1], excInfo[2])
            finally:
                excInfo = None
        elif self.header_sent:
            raise AssertionError("Headers already set!")

        self.response_status = status
        self.response_headers = ResponseHeaders(response_headers)
        return self.write

    def write(self, data):
        if not self.response_status:
            raise AssertionError("write() before start_response()")
        if not self.header_sent:
            self.bytes_sent = len(data)
            self.send_headers()
        else:
            self.bytes_sent += len(data)

        self.__write(data)
        self.__flush()

    def send_headers(self):
        """ Send response header to client """
        self.header_sent = True
        self.setup_header()

        self.send_preamble()
        self.__write(self.response_headers)

    def setup_header(self):
        """ Make necessary header changes """
        if "Content-Length" not in self.response_headers:
            self.set_content_length()

    def set_content_length(self):
        """ Get the Content-Length if possible """
        if 'Content-Length' not in self.response_headers:
            try:
                blocks = len(self.result)
            except (TypeError, AttributeError, NotImplementedError):
                self.response_headers["Content-Length"] = str(self.bytes_sent)
            else:
                if blocks == 1:
                    self.response_headers["Content-Length"] = str(self.bytes_sent)

    def send_preamble(self):
        """ Send version/status/date/server to client """
        self.__write('HTTP/%s %s\r\n' % (self.version, self.response_status))
        if "Date" not in self.response_headers:
            self.__write("Date: %s\r\n" % format_date_time(time.time()))

        if self.server.server_software and "Server" not in self.response_headers:
            self.__write("Server: %s\r\n" % self.server.server_software)

    def finish_response(self):
        """ Send the iterable data, then close self and the iterable data
        """
        try:
            for data in self.result:
                self.write(data)
            self.finish_content()
        finally:
            self.close()

    def finish_content(self):
        """Ensure headers and content have both been sent"""
        if not self.header_sent:
            # Only zero Content-Length if not set by the application (so
            # that HEAD requests can be satisfied properly, see #3839)
            if self.response_headers.get('Content-Length') is None:
                self.response_headers.add_header('Content-Length', 0)
            self.send_headers()
        else:
            pass  # XXX check if content-length was too short?

    def handle_error(self):
        """ Send error output to client if possible """
        self.log_exception(sys.exc_info())
        if not self.header_sent:
            self.result = self.error_output(self.environ, self.start_response)
            self.finish_response()

    def log_exception(self, exc_info):
        """
        Log the exc_info to server log by stderr
        Can override this method to change the format
        :param exc_info:
        """
        try:
            print_exception(exc_info[0], exc_info[1], exc_info[2], None, self.stderr)
        finally:
            exc_info = None

    def error_output(self, environ, start_response):
        """

        :param environ:
        :param start_response:
        :return error_body:
        """
        start_response(self.error_status, self.error_headers, sys.exc_info())
        return [self.error_body]

    def set_stderr(self, stderr):
        """
        Set the stderr for error out put
        :param stderr:
        :return:
        """
        self.stderr = stderr

    def __write(self, data):
        self.wfile.write(data)
        self._write = self.wfile.write

    def __flush(self):
        self.wfile.flush()
        self._flush = self.wfile.flush


class SimpleResponse(object):
    """
    The response class to build a reponse to client
    """
    RESPONSE_STATUS = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        }

    @staticmethod
    def get_status_phrase(status):
        return SimpleResponse.RESPONSE_STATUS.get(status)[0]

    def __init__(self, status, version, headers, body=None):
        self.status = status
        self.version = version
        self.headers = headers
        self.body = body

    def to_string(self):
        output = StringIO.StringIO()

        # write start line
        output.write(str(self.version))
        output.write(' ')
        output.write(str(self.status))
        output.write(' ')
        output.write(str(SimpleResponse.get_status_phrase(self.status)))
        output.write('\r\n')

        # write header
        for header, value in self.headers:
            output.write(str(header))
            output.write(': ')
            output.write(str(value))
            output.write('\r\n')

        output.write('\r\n')

        # write body
        if self.body is not None:
            output.write(str(self.body))

        return output.getvalue()

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


class WSGIServer(object):

    server_software = "Test Server"

    def __init__(self, handler, host=None, port=None):
        self.host = host
        self.port = port
        self.handler = handler

        self.server_name = ""

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.base_environ = {}

        if host is not None and port is not None:
            self.__socket.bind((host, port))
            self.server_name = socket.getfqdn(host)
            self.setup_environ()

        self.__socket.listen(2)

        self.running = False

        self.application = None

    def start(self):
        while True:
            conn, addr = self.__socket.accept()
            rfile = conn.makefile("rb")
            wfile = conn.makefile("wb")
            request_handler = self.handler(self, rfile, wfile, addr)

            request_handler.handle_one_request()
            conn.close()

    def bind(self, host, port):
        """ Bind host and port to server socket """
        if self.__running is False:
            self.__socket.bind((host, port))
            self.server_name = socket.getfqdn(host)
            self.setup_environ()

    def close(self):
        """ Close server socket """
        self.running = False
        self.__socket.close()

    def set_app(self, application):
        """ Set server app """
        self.application = application

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''
        env['HTTPS'] = 'off'


if __name__ == "__main__":
    server = WSGIServer(WSGIRequest, "", 8887)
    # server = WSGIServer(HTTPRequest, '', 8888)
    from server.djangoapp import app
    atexit.register(server.close)
    server.set_app(app)
    print("start")
    server.start()
