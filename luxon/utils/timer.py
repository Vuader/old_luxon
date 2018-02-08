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

import datetime
from timeit import default_timer
from contextlib import contextmanager

from luxon import GetLogger

log = GetLogger(__name__)

debug_mode = log.debug_mode


class Timer():
    """Code Execution Timer.

    Wrap code in execution timer to see elasped time.

    **Example**

    .. code:: python

        with timer() as elapsed:
            time.sleep(1)
            print(elapsed())
            time.sleep(2)
            print(elapsed())
            time.sleep(3)
        print(elapsed())
    """

    # NOTE(cfrademan): Yes this is pretty strange way going about it.
    # However good performance is gained over using yield with contextlib.
    # In this case the pattern wins since we use timers in many parts of
    # the framework.
    def __enter__(self):
        start = default_timer()

        def timed():
            try:
                return self.end
            except AttributeError:
                return default_timer() - start

        if debug_mode():
            self.timed = timed
        else:
            self.timed = lambda: None
            return lambda: None

        return timed

    def __exit__(self, type, value, traceback):
        self.end = self.timed()
