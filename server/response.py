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
from server import SERVER

from server.header import ResponseHeaders
from server.header import format_date_time

try:
    import cStringIO as StringIO
except (Exception, ):
    import StringIO


class HttpResponse(object):
    """
    The base class for response
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

    def __init__(self, status, header, result=None):
        self.status = status
        self.header = header
        self.result = result

        self.wfile = None

    def set_wfile(self, wfile):
        self.wfile = wfile


class SimpleResponse(object):
    """
    The response class to build a response to client
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
        oputstr = output.getvalue()
        output.close()
        return oputstr

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


class WsgiResponse(object):

    def __init__(self, status, headers, result):
        self.status = status
        self.headers = headers
        self.result = result

        self.bytes_sent = 0

        # The flag to indicate if headers send client
        self._send_header = False

        self.wfile = None

        self.version = "1.1"

    def set_wfile(self, wfile):
        self.wfile = wfile

    def handle_response(self):
        """

        :return:
        """
        self.headers = ResponseHeaders.get_headers(self.headers)
        self.finish_response()

    def finish_response(self):
        """ Send the iterable data, then close self and the iterable data
        """
        # try:
        for data in self.result:
            self.write(data)
        # finally:
        #     self.close()

    def write(self, data):
        if not self._send_header:
            self.bytes_sent = len(data)
            self.send_headers()
        else:
            self.bytes_sent += len(data)

        self.__write(data)
        self.__flush()

    def send_headers(self):
        """ Send response preamble and header  to client"""
        self._send_header = True
        self.setup_headers()

        self.send_preamble()
        self.__write(self.headers)

    def setup_headers(self):
        """ Make necessary header here """
        if 'Content-Length' not in self.headers:
            self.set_content_length()

    def set_content_length(self):
        """ Set Content-Length in header """
        if 'Content-Length' not in self.headers:
            try:
                length = len(self.result)
            except (TypeError, AttributeError, NotImplementedError):
                self.headers["Content-Length"] = str(self.bytes_sent)
            else:
                if length == 1:
                    self.headers["Content-Length"] = str(self.bytes_sent)

    def send_preamble(self):
        """ Send version/status/date/server to client """
        self.__write('HTTP/%s %s\r\n' % (self.version, self.status))
        if "Date" not in self.headers:
            self.__write("Date: %s\r\n" % format_date_time(time.time()))

        if SERVER and "Server" not in self.headers:
            self.__write("Server: %s\r\n" % SERVER)

    def __write(self, data):
        self.wfile.write(data)
        self.__write = self.wfile.write

    def __flush(self):
        self.wfile.flush()
        self.__flush = self.wfile.flush