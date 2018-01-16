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

from luxon import g
from luxon import GetLogger
from luxon.utils import js
from luxon.core.policy import compiler
from luxon.core.policy import Policy as PolicyEngine
from luxon.exceptions import AccessDenied

log = GetLogger(__name__)

class Policy(object):
    __slots__ = ( '_compiled' )

    def __init__(self):
        app_root = g.app.app_root

        # Compile the policies if policy.json found.
        if os.path.isfile(app_root + '/policy.json'):
            policy_file = open(app_root + '/policy.json', 'r')
            rule_set = js.loads(policy_file.read())
            self._compiled = compiler(rule_set)
        else:
            log.warning("No 'policy.json' found in '" + app_root + "/policy.json'" +
                        " compiling empty rule set")
            self._compiled = compiler({})

    def resource(self, req, resp):
        # Load policy for request.
        req.policy = policy = PolicyEngine(self._compiled, req=req)
        tag = req.tag

        if tag is not None and not policy.validate(tag):
            raise AccessDenied("Access Denied by Policy" +
                               " Rule '%s'" % tag +
                               " Route '%s'" % req.route +
                               " Method '%s'" % req.method)
