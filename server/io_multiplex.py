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

import select
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s : ',
                    datefmt='%a, %d %b %Y %H:%M:%S')

EPOLLIN = 0x001
EPOLLPRI = 0x002
EPOLLOUT = 0x004
EPOLLRDNORM = 0x040
EPOLLRDBAND = 0x080
EPOLLWRNORM = 0x100
EPOLLWRBAND = 0x200
EPOLLMSG = 0x400
EPOLLERR = 0x008
EPOLLHUP = 0x010
EPOLLONESHOT = (1 << 30)
EPOLLET = (1 << 31)


class IOMultiplex(object):

    __multiplex = None

    READ = EPOLLIN | EPOLLPRI | EPOLLRDNORM
    WRITE = EPOLLOUT | EPOLLWRNORM
    ERROR = EPOLLERR | EPOLLHUP | EPOLLMSG

    @classmethod
    def __initialized(cls):

        cls.__multiplex = cls.__multiplex if cls.__multiplex is not None else IOMultiplex()
        return cls.__multiplex

    @classmethod
    def initialized(cls):
        return cls.__initialized()

    def __init__(self):
        self.loop = _epoll()

        self.__events = {}
        self._handler = {}

        self.running = False

        self.timeout = 1

    def add_handler(self, fd, handler, eventmask):
        self._handler[fd] = handler
        self.loop.register(fd, eventmask)

    def remove_handler(self, fd):
        del self._handler[fd]
        self.loop.unregister(fd)

    def start(self):
        self.running = True

        while self.running:
            events = self.loop.poll(self.timeout)
            self.__events = events

            for fd, event in self.__events.items():
                try:
                    self._handler[fd](fd, event)
                except Exception as ex:
                    logging.error(str(ex))

    def stop(self):
        self.running = False


class _Select(object):

    def __init__(self):
        self.read_set = set()
        self.write_set = set()
        self.error_set = set()

    def register(self, fd, eventmask):
        if eventmask & IOMultiplex.READ:
            self.read_set.add(fd)
        elif eventmask & IOMultiplex.WRITE:
            self.write_set.add(fd)
        elif eventmask & IOMultiplex.ERROR:
            self.error_set.add(fd)

    def modify(self, fd, eventmask):
        if fd in self.read_set and (eventmask & IOMultiplex.READ) == False:
            self.read_set.remove(fd)

        if fd in self.write_set and (eventmask & IOMultiplex.WRITE) == False:
            self.read_set.remove(fd)

        if fd in self.error_set and (eventmask & IOMultiplex.ERROR) == False:
            self.read_set.remove(fd)

        self.register(fd, eventmask)

    def unregister(self, fd):
        if fd in self.read_set:
            self.read_set.remove(fd)

        if fd in self.write_set:
            self.read_set.remove(fd)

        if fd in self.error_set:
            self.read_set.remove(fd)

    def poll(self, timeout):
        read_list, write_list, error_list = select.select(self.read_set, self.write_set, self.error_set, timeout)

        events = {}

        for fd in read_list:
            events[fd] = events.get(fd, 0) | IOMultiplex.READ

        for fd in write_list:
            events[fd] = events.get(fd, 0) | IOMultiplex.WRITE

        for fd in error_list:
            events[fd] = events.get(fd, 0) | IOMultiplex.ERROR

        return events


if hasattr(select, "epoll"):
    _epoll = select.epoll
elif hasattr(select, "poll"):
    _epoll = select.poll
else:
    _epoll = _Select


if __name__ == "__main__":
    m = IOMultiplex.initialized()
    m.start()