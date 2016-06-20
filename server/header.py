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
from types import ListType

# Weekday and month names for HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [None, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )


class Headers(object):
    """ The basic header class to manage the request or response header """
    def __init__(self):
        self.headers = {}

    def __len__(self):
        """ return the number of headers """
        return len(self.headers) if self.headers is not None else 0

    def __setitem__(self, key, value):
        """ set a header """
        self.headers[key] = value

    def __getitem__(self, item):
        """ get a header, if not exist than return None """
        return self.headers.get(item)

    def __delitem__(self, key):
        """ remove a header """
        if self.headers.get(key) is not None:
            del self.headers[key]

    def get(self, header, default=None):
        """
        Get a header value, if header not exist return the default value
        :param header: the header name
        :param default: the default value
        :return:
        """
        return self.headers.get(header, default)

    def keys(self):
        """
        return the list of header name
        :return:
        """
        return self.headers.keys()

    def set_header(self, key, value):
        """ set a header"""
        self.headers[key] = value

    def has_key(self, key):
        """ return True if has this header else return False """
        return self.headers.has_key(key)

    def __str__(self):
        return '\r\n'.join(["%s: %s" % (k, v) for k, v in self.headers.items()] + ['', ''])

        # class ResponseHeaders(object):
#     """ The class to manage the response headers """
#     def __init__(self, headers):
#         if type(headers) is not ListType:
#             raise TypeError("Header must be a list of name/value tuples")
#
#         self.__headers = headers
#
#     def __len__(self):
#         """ return the number of headers """
#         return len(self.__headers)
#
#     def __setitem__(self, key, value):
#         """ Set a header """
#         del self[key]
#         self.__headers.append((key, value))
#
#     def __delitem__(self, key):
#         """ Delete a header """
#         key = key.lower()
#         self.__headers[:] = [kv for kv in self.__headers if kv[0].lower != key]
#
#     def __getitem__(self, item):
#         """ Return the value of the header by key.
#          If no such header, return NULL
#          """
#         return self.get(item)
#
#     def get(self, name, default=None):
#         """ Get the header by name , if not exist reutn 'default' """
#         name = name.lower()
#         for k, v in self.__headers:
#             if k.lower() == name:
#                 return v
#         return default
#
#     def has_key(self, name):
#         """ Retrun ture if has this header """
#         name = name.lower()
#         return self.get(name) is not None
#
#     __contains__ = has_key
#
#     def keys(self):
#         return [k for k, v in self.__headers]
#
#     def values(self):
#         return [v for k, v in self.__headers]
#
#     def items(self):
#         return self.__headers[:]
#
#     def add_header(self, name, value):
#         if self.has_key(name):
#             del self.__headers[name]
#
#         self.__headers.append((name, value))
#
#     def __str__(self):
#         return '\r\n'.join(["%s: %s" % kv for kv in self.__headers] + ['', ''])
