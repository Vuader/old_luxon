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

from luxon.core.cls.nullerror import NullError
from luxon.exceptions import NoContextError
from luxon.utils.objects import object_name
from luxon.structs.threaddict import ThreadDict

_thread_globals = ThreadDict()
_thread_items = ('current_request',)

_context_items = ('app',
                  'current_request',
                 )

_middleware_pre = []
_middleware_resource = []
_middleware_post = []


class Globals(object):
    """Global object providing unique thread object references to.

    Purpose:
        * Placeholder for context related references.
        * Ensures some references to objects are based on thread.

    Args:
        global_name (str): Uniquely identify the global.
        obj (any): Any object you wish to proxy.
    """
    __slots__ = ( '__dict__' )

    @property
    def middleware_pre(self):
        return _middleware_pre

    @property
    def middleware_resource(self):
        return _middleware_resource

    @property
    def middleware_post(self):
        return _middleware_post

    @property
    def router(self):
        global _cached_global_router

        try:
            return _cached_global_router
        except NameError:
            from luxon.core.router import Router
            _cached_global_router = Router()
            return _cached_global_router

    def __setitem__(self, key, value):
        if key in _thread_items:
            _thread_globals[key] = value
        else:
            self.__dict__[key] = value

    def __delitem__(self, key):
        try:
            del _thread_globals[key]
        except KeyError:
            try:
                del self.__dict__[key]
            except KeyError:
                raise KeyError("'" + object_name(self) +
                               "' object has no key '" +
                               key + "'") from None

    def __getitem__(self, key):
        try:
            return _thread_globals[key]
        except KeyError:
            try:
                return self.__dict__[key]
            except KeyError:
                if key in _context_items:
                    # Place holder for context - Provides nice error.
                    return NullError(NoContextError,
                                     "Working outside of '%s'" % key +
                                     " context")
                raise KeyError("'" + object_name(self) +
                               "' object has no key '" +
                               key + "'") from None

    def __setattr__(self, key, value):
        if key in _thread_items:
            _thread_globals[key] = value
            return True

        self.__dict__[key] = value

        return True

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("'" + object_name(self) +
                                 "' object has no '" +
                                 attr + "'") from None

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError("'" + object_name(self) +
                                 "' object has no '" +
                                 attr + "'") from None

    def __contains__(self, key):
        return key in _thread_globals or key in self.__dict__


# All globals.... luxon.g = Application wide context.
luxon_globals = Globals()
