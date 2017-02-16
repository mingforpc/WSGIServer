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

from traceback import print_exception
from server.header import ResponseHeaders, RequestHeaders
from server.header import format_date_time
from server.response import SimpleResponse

import logging
import time
import sys

try:
    import cStringIO as StringIO
except (Exception, ):
    import StringIO

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s : ',
                    datefmt='%a, %d %b %Y %H:%M:%S')

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
            logging.error(ex)
            self.send_simple_response(500)
        finally:
            self.close()

    def parse_request(self):
        """
        Parse the http struct from 'rfile'
        """
        start_line = self.rfile.readline(HTTPRequest.MAX_URL_SIZE)
        start_line = start_line.replace('\r\n', '\n').replace('\r', '\n')
        logging.debug(start_line)
        self.commond, self.path, self.query, self.version = HTTPRequest.__parse_startline(start_line)

        self.headers = RequestHeaders(HTTPRequest.__parse_header(self.rfile))
        logging.debug(self.headers)

        # Process 'Expect' header with value "100-continue"
        if self.headers.get("Expect") is not None and self.headers.get("Expect") == "100-continue":
            self.send_simple_response(100)

        content_length = int(self.headers.get("Content-Length", 0))
        self.body = HTTPRequest.__parse_body(self.rfile, content_length)
        logging.debug(self.body.getvalue())

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
        body = StringIO.StringIO()
        if content_length != 0 and content_length <= HTTPRequest.MAX_BODY_SIZE:
            body.write(rfile.read(content_length))

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

    def send_simple_response(self, status, header=[('Content-Type', 'text/plain',), ]):
        """
        Return a simple response to client
        :param status: the status code
        :param header: http header
        :return:
        """
        response = SimpleResponse(status, self.version, header, "")
        self.__write(response)
        self.__flush()


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
        environ["wsgi.input"] = self.body
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
        logging.debug(response_headers)
        self.response_headers = ResponseHeaders.get_headers(response_headers)
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
                self.response_headers.set_header('Content-Length', 0)
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