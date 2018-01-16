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
from luxon.exceptions import AccessDenied
from luxon.utils.imports import get_class

log = GetLogger(__name__)

class Token(object):
    """Tokens Responders / Views.

    Luxon tokens use PKI. Its required to have the private key to sign
    new tokens on the tachyonic api. Endpoints will require the public cert
    to validate tokens authenticity.

    The tokens should be stored in the application root. Usually where the wsgi
    file is located.

    Creating token:
        openssl req  -nodes -new -x509  -keyout token.key -out token.cert

    """
    __slots__ = ()

    def pre(self, req, resp):
        driver = g.app.config.get('tokens','driver')
        expire = g.app.config.getint('tokens','expire')
        req.context.token = get_class(driver)(expire)
        token = req.get_header('X-Auth-Token')
        if token is not None:
            req.context.token.parse_token(token)

        req.context.domain = req.get_header('X-Domain', default='default')
        req.context.tenant_id = req.get_header('X-Tenant-Id')
        req.context.roles = req.context.token.roles(req.context.domain,
                                                    req.context.tenant_id)
        log.error(req.context.roles)

