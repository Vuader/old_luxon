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
from getpass import getpass

from luxon import g
from luxon import GetLogger
from luxon.exceptions import AccessDenied
from luxon.utils.imports import get_class
from luxon.api.client import Client

log = GetLogger(__name__)

class Auth(object):
    __slots__ = ()

    def pre(self, req, resp):
        if 'TAC_API' not in os.environ:
            raise AccessDenied('Require Tachyonic URI (TAC_API system' +
                               ' environment)')

        print('API: %s' % os.environ['TAC_API'])

        if 'TAC_DOMAIN' not in os.environ:
            domain = None
            print('Domain: -*Global*-')
        else:
            domain = os.environ['TAC_DOMAIN']
            print('Domain: %s' % domain)

        if 'TAC_USER' not in os.environ:
            raise AccessDenied('Require Tachyonic Username (TAC_USER system' +
                               ' environment)')

        print('Username: %s' % os.environ['TAC_USER'])


        if 'TAC_TENANT_ID' not in os.environ:
            tenant_id = None
        else:
            tenant_id = os.environ['TAC_TENANT_ID']

        g.api = api = Client(os.environ['TAC_API'])

        password = getpass(prompt='Password: ')
        print('')

        api.authenticate(os.environ['TAC_USER'],
                         password,
                         domain)

        api.scope(domain, tenant_id)
