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

from server.http import WSGIServer
from server.request import WSGIRequest
from server.io_multiplex import IOMultiplex

import atexit

if __name__ == "__main__":
    server = WSGIServer("0.0.0.0", 8889)
    server.set_blocking(0)
    # server = WSGIServer(HTTPRequest, '', 8888)
    from test.helloworld.helloworld.wsgi import application as app
    atexit.register(server.close)
    server.set_app(app)
    print("start")
    server.start()
    print("IO Started")
    IOMultiplex.initialized().start()
