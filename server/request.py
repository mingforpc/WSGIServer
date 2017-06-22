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
from server import SERVER
from server.err_code import ERR_SUCCESS, ERR_NULL_REQUEST, ERR_INTERNAL_EXCEPTION, ERR_100_CONTINUE_REQUEST
from server.err_code import get_err_msg
from server.header import RequestHeaders
from server.response import WsgiResponse
from server.exception.request_exception import ReadBlankException, RequestContinueException

import sys

from server.log import logging

try:
    import cStringIO as StringIO
except (Exception, ):
    import StringIO


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

        self.content_length = None
        # request body
        self.body = None

    def handle_one_request(self):
        err = ERR_SUCCESS
        err_msg = get_err_msg(ERR_SUCCESS)
        response = None
        try:
            self.parse_request()
            response = self.handle_request()
        except ReadBlankException as ex:
            # Get blank request
            err = ERR_NULL_REQUEST
            err_msg = get_err_msg(err)
        except RequestContinueException as ex:
            # Get 100 continue request
            err = ERR_100_CONTINUE_REQUEST
            err_msg = get_err_msg(err)
            response = WsgiResponse.make_response(100)
        except Exception as ex:
            # print log here
            logging.error("Exception while parse request: %s", ex)
            err = ERR_INTERNAL_EXCEPTION
            err_msg = get_err_msg(err)
            response = WsgiResponse.make_response(500)

        finally:
            return err, err_msg, response

    def handle_100_continue(self):
        """
        Process after get 100 continue header. Read body from steam
        :return:
        """
        err = ERR_SUCCESS
        err_msg = get_err_msg(ERR_SUCCESS)
        response = None

        self.body = HTTPRequest.__parse_body(self.rfile, self.content_length)
        logging.debug("request body: %s", self.body.getvalue())

        try:
            self.parse_request()
            response = self.handle_request()
        except Exception as ex:
            # print log here
            logging.error("Exception while parse request: %s", ex)
            err = ERR_INTERNAL_EXCEPTION
            err_msg = get_err_msg(err)
            response = WsgiResponse.make_response(500)
        finally:
            return err, err_msg, response

    def parse_request(self):
        """
        Parse the http struct from 'rfile'
        """

        start_line = self.rfile.readline(HTTPRequest.MAX_URL_SIZE)
        start_line = start_line.replace('\r\n', '\n').replace('\r', '\n')
        logging.debug("start_line: %s", start_line)

        # Check if read blank string
        if start_line == "":
            raise ReadBlankException("Get blank data from client socket")

        self.commond, self.path, self.query, self.version = HTTPRequest.__parse_startline(start_line)

        self.headers = RequestHeaders(HTTPRequest.__parse_header(self.rfile))
        logging.debug("header: %s", self.headers)

        self.content_length = int(self.headers.get("Content-Length", 0))

        # Process 'Expect' header with value "100-continue"
        if self.headers.get("Expect") is not None and self.headers.get("Expect") == "100 Continue":
            # self.send_simple_response(100)
            raise RequestContinueException("Get 100 continue request")

        self.body = HTTPRequest.__parse_body(self.rfile, self.content_length)
        logging.debug("request body: %s", self.body.getvalue())

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
            a = ''
            headers[header] = value.strip('\r\n').strip('\n').strip()

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

    # def send_simple_response(self, status, header=[('Content-Type', 'text/plain',), ]):
    #     """
    #     Return a simple response to client
    #     :param status: the status code
    #     :param header: http header
    #     :return:
    #     """
    #     response = SimpleResponse(status, self.version, header, "")
    #     self.__write(response)
    #     self.__flush()


class WSGIRequest(HTTPRequest):

    def __init__(self, server, rfile, wfile, addr):
        super(WSGIRequest, self).__init__(server, rfile, wfile, addr)

        self.application = server.application
        self.environ = None

        self.stderr = None

        self.result = None
        self.response_status = None
        self.response_headers = None

    def handle_request(self):
        """
        Call the function run() to invoke wsgi application
        :return:
        """
        response = self.run()
        return response

    def run(self):

        try:
            environ = self.getenv()
            self.result = self.application(environ, self.start_response)
            response = WsgiResponse(self.response_status, self.response_headers, self.result)
        except (Exception, ) as ex:
            logging.error('Exception in run(): %s', ex)
            response = WsgiResponse.make_response(500)

        finally:
            return response

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

        environ['SERVER_SOFTWARE'] = SERVER

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
                raise(excInfo[0], excInfo[1], excInfo[2])
            finally:
                excInfo = None

        self.response_status = status
        logging.debug("response header: %s", response_headers)
        self.response_headers = response_headers
        return self.write

    # def handle_error(self):
    #     """ Send error output to client if possible """
    #     self.log_exception(sys.exc_info())
    #     self.result = self.error_output(self.environ, self.start_response)

    # def log_exception(self, exc_info):
    #     """
    #     Log the exc_info to server log by stderr
    #     Can override this method to change the format
    #     :param exc_info:
    #     """
    #     try:
    #         print_exception(exc_info[0], exc_info[1], exc_info[2], None, self.stderr)
    #     finally:
    #         exc_info = None
