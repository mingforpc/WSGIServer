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
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import logging
import sys

logger = logging.getLogger("server_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                              datefmt='%a, %d %b %Y %H:%M:%S')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

sys.modules[__name__] = logger
