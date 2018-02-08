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
import hashlib
import traceback
import pickle
from time import time

from decorator import decorator

from luxon import g
from luxon.core.logger import GetLogger
from luxon.structs.models.fields import BaseField
from luxon.helpers.redis import strict
from luxon.utils.encoding import if_unicode_to_bytes
from luxon.exceptions import NoContextError
from luxon.utils.objects import object_name

log = GetLogger(__name__)


class Cache(object):
    def __init__(self):
        try:
            redis = g.config.get('redis', 'host', fallback=None)
            if redis is not None:
                self.redis = strict()
            else:
                self.redis = None
        except NoContextError:
            self.redis = None

    def store(self, reference, obj, expire):
        if self.redis is not None:
            reference = if_unicode_to_bytes(reference)
            ref = hashlib.md5(reference).hexdigest()
            name = 'cache:%s' % ref
            self.redis.set(name, pickle.dumps(obj), ex=expire)

    def load(self, reference):
        if self.redis is not None:
            reference = if_unicode_to_bytes(reference)
            ref = hashlib.md5(reference).hexdigest()
            name = 'cache:%s' % ref
            cached = self.redis.get(name)
            if cached is not None:
                return pickle.loads(cached)
            else:
                return None
        else:
            return None


def memoize(expiry_time=0, num_args=None):
    def _memoize(func, *args, **kw):
        cache = Cache()

        mem_args = args[:num_args]
        # frozenset is used to ensure hashability
        if kw:
            key = object_name(func), mem_args, frozenset(kw.iteritems())
        else:
            key = object_name(func), mem_args
        key = pickle.dumps(key)

        cached = cache.load(key)
        if cached is not None:
            return cached
        result = func(*args, **kw)
        cache.store(key, result, expiry_time)
        return result

    return decorator(_memoize)
