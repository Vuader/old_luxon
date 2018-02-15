# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import os
import threading
import random

from luxon import g
from luxon import GetLogger
from luxon.utils.unique import string_id
from luxon.structs.container import Container
from luxon.utils.imports import get_class


log = GetLogger(__name__)

req_c = None
proc_ids = {}
pid = None

def request_id():
    # Using random is pretty slow. This is way quicker.
    # It uses cached proc_id which uses random once for PID.
    # Then only does this append a counter.
    # It may not be as unique, but highly unlikely to collide
    # with recent requet ids.
    global req_c, pid
    if req_c is None:
        req_c = random.randint(1000*1000, 1000*1000*1000)

    if pid is None:
        pid = str(os.getpid())
    try:
        proc_id = proc_ids[pid]
    except KeyError:
        proc_id = proc_ids[pid] = string_id(6)

    req_id = req_c = req_c + 1
    req_id = hex(req_id)[2:].zfill(8)[-8:]

    return proc_id + '-' + req_id

class RequestBase(object):
    """Base Class Represents a client's request.

    Args:
        *: All other args are for specific initilization of parent classes.

    Keyword Args:
        *: All other kwargs are for specific initilization of parent classes.

    Attributes:
        id (string):
            Unique request identifier.
        method (str): Route Method for determining routing to view.
        route (str): Path portion of the request for routing to view.
        tag (str): Route tag, used by policies to apply rules.
        context: Dictionary/Property object to hold any data about the
            request which is specific to your app. (e.g. auth object)
        log: Dictionary/Property object to hold any data about the
            request which is specific to your app for appending to logs.
            (e.g. USERNAME)
    """
    __slots__ = (
        'app',
        'route',
        'route_kwargs',
        'method',
        'log',
        'id',
        'policy',
        'tag',
        'context',
        'response',
        '_cached_token',
    )
    def __init__(self, *args, **kwargs):
        # Request ID
        self.id = id = request_id()

        self.log = {}
        self.log['REQUEST-ID'] = id

        # Request Context
        self.context = Container()

        self.response = None

        self._cached_token = None

    def __repr__(self):
        return '<%s: %s %r>' % (self.__class__.__name__, self.method,
                                self.route)

    def __str__(self):
        return '<%s: %s %r>' % (self.__class__.__name__, self.method,
                                self.route)

    @property
    def token(self):
        if self._cached_token is None:
            driver = g.app.config.get('tokens','driver')
            expire = g.app.config.getint('tokens','expire')
            self._cached_token = get_class(driver)(expire)
        return self._cached_token
