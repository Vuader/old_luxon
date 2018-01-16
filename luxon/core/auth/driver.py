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
import base64
from datetime import timedelta

from luxon import g
from luxon.utils.password import valid as is_valid_password
from luxon.utils import js
from luxon.utils.timezone import now
from luxon.structs.container import Container
from luxon.utils import pki
from luxon.utils.encoding import if_unicode_to_bytes, if_bytes_to_unicode
from luxon.exceptions import AccessDenied
from luxon import GetLogger

log = GetLogger(__name__)

from hashlib import md5

class BaseDriver(object):
    """Base Authentication BaseDriver

    Behaves like a dictionary and provides convienance methods to build
    expected environment structure for API Context.

    During authentication calls, its required to update the Request Object
    context with values stored in authentication environment. To achieve this
    its required that the Authentication driver provides a dictionary object.
    Even though it behaves like one it cannot be used to update another
    dictionary. Therefor its callable and returns a dict object with all
    values.

    Its recomended to use the methods to create the environment.

    Args:
        expire (int): Seconds to expire token.
    """
    def __init__(self, expire=3600):
        self._token_expire = expire
        self._initial()

    def new_token(self, user_id, username, domain, domain_id,
              roles=[], tenant_id=None):
        """Create Token.

        This part of step 1 during the authentication after validation.

        Args:
            user_id (str): User ID
            username (str): Username.
            email (str): User email address.
            token (str): Unique token for specific user.
            domain_id (str): Current domain id.
            tenant_id (str): Current tenant id.
        """
        if self._token is not None:
            raise ValueError('Token readonly after authenticated')
        self._token = {}

        # These are only set during valid login.
        # Unique user id.
        self._token['user_id'] = user_id

        # Unique username.
        self._token['username'] = username

        # Token creation datetime, format YYYY/MM/DD HH:MM:SS.
        self._token['creation'] = now()

        # Token expire datetime, format YYYY/MM/DD HH:MM:SS.
        expire = (now() + timedelta(seconds=self._token_expire))
        self._token['expire'] = expire.strftime("%Y/%m/%d %H:%M:%S")

        # User belongs to this domain.
        self._token['user_domain'] = domain
        self._token['user_domain_id'] = domain_id

        # User belongs to this tenant.
        self._token['user_tenant_id'] = tenant_id

        # User has following roles assigned.
        self._token['user_roles'] = {}

        for role in roles:
            role_name, domain, tenant_id = role
            if role_name not in self._token['user_roles']:
                self._token['user_roles'][role_name] = {}
                self._token['user_roles'][role_name]['domains'] = []
                self._token['user_roles'][role_name]['tenants'] = []
            if domain not in self._token['user_roles'][role_name]['domains']:
                self._token['user_roles'][role_name]['domains'].append(domain)
            if tenant_id not in self._token['user_roles'][role_name]['tenants']:
                self._token['user_roles'][role_name]['tenants'].append(tenant_id)

        # Token Signature
        private_key = g.app.app_root.rstrip('/') + '/token.key'
        bytes_token = if_unicode_to_bytes(js.dumps(self._token))
        self._token_sig = pki.sign(private_key, base64.b64encode(bytes_token))
        return self._token_sig

    def roles(self, domain, tenant_id=None):
        roles = []
        token = self.token
        if token is not None:
            for role in token['user_roles']:
                if domain in token['user_roles'][role]['domains']:
                    if tenant_id is None:
                        roles.append(role)
                    elif tenant_id in token['user_roles'][role]['tenants']:
                        roles.append(role)
                elif tenant_id in token['user_roles'][role]['tenants']:
                    roles.append(role)
        return roles

    @property
    def token(self):
        if self._token is not None and self._cached_token is None:
            self._cached_token = self._token.copy()
            self._cached_token['token'] = if_unicode_to_bytes(self._token_sig) \
                + b'!!!!' + \
                if_unicode_to_bytes(base64.b64encode(
                    if_unicode_to_bytes(js.dumps(self._token))))
        return self._cached_token

    @property
    def encoded(self):
        return self.token['token']

    def __len__(self):
        return len(self.token['token'])

    def __str__(self):
        if self.token is None:
            return '{}'
        else:
            return js.dumps(self.token)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    def _initial(self):
        """Default Values.
        """
        self._token = None
        self._token_sig = None
        self._cached_token = None
        self._context = Container()

    def clear(self):
        """Clear Login Context.
        """
        self._initial()

    def authenticate(self, username, password, domain='default'):
        return False

    def login(self, username, password, domain='default'):
        if self.authenticate(username, password, domain):
            return True
        else:
            log.warning('Invalid login credentials for %s' % username)
            raise AccessDenied('Invalid login credentials')

    def parse_token(self, token):
        self._initial()
        token = if_unicode_to_bytes(token)
        signature, token = token.split(b'!!!!')
        cert = g.app.app_root.rstrip('/') + '/token.cert'
        try:
            self._token_sig = pki.verify(cert, signature, token)
        except ValueError as e:
            log.warning('Invalid Token: %s' % e)
            raise AccessDenied('Invalid Token')
        self._token = js.loads(base64.b64decode(token))
        self._token_sig = signature
