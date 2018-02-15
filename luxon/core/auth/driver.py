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
from hashlib import md5

from luxon import g
from luxon.utils import js
from luxon.utils.timezone import now, utc
from luxon.structs.container import Container
from luxon.utils import pki
from luxon.utils.encoding import if_unicode_to_bytes, if_bytes_to_unicode
from luxon.exceptions import AccessDenied
from luxon import GetLogger
from luxon.utils.auth import context_roles
from luxon.utils.cast import to_tuple

log = GetLogger(__name__)



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

    def new_token(self, user_id, username, domain=None, tenant_id=None,
                  expire=None, roles=[]):
        """Create Token.

        This part of step 1 during the authentication after validation.

        Args:
            user_id (str): User ID
            username (str): Username.
            email (str): User email address.
            token (str): Unique token for specific user.
            tenant_id (str): Current tenant id.
        """
        self._token = {}
        if user_id is None:
            raise ValueError('Require user_id for new_token')
        if username is None:
            raise ValueError('Require username for new_token')

        # These are only set during valid login.
        # Unique user id.
        self._token['user_id'] = user_id

        # Unique username.
        self._token['username'] = username

        # Token creation datetime, format YYYY/MM/DD HH:MM:SS.
        self._token['creation'] = now()

        # Token expire datetime, format YYYY/MM/DD HH:MM:SS.
        if expire is None:
            expire = (now() + timedelta(seconds=self._token_expire))
            self._token['expire'] = expire.strftime("%Y/%m/%d %H:%M:%S")
        else:
            self._token['expire'] = expire

        # Scope domain.
        self._token['domain'] = domain

        # Scope tenant.
        self._token['tenant_id'] = tenant_id

        # Scope roles.
        self._token['roles'] = list(set(context_roles(user_id,
                                        domain,
                                        tenant_id) + roles))

        # Token Signature
        private_key = g.app.app_root.rstrip('/') + '/token.key'
        bytes_token = if_unicode_to_bytes(js.dumps(self._token))
        self._token_sig = pki.sign(private_key, base64.b64encode(bytes_token))
        return self._token_sig

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
    def authenticated(self):
        if self._token is not None:
            return True
        else:
            return False

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

    @property
    def json(self):
        return self.__str__()

    def _initial(self):
        """Default Values.
        """
        self._token = None
        self._token_sig = None
        self._cached_token = None
        self._tenant_id = None
        self._domain = None

    def clear(self):
        """Clear Login Context.
        """
        self._initial()

    def authenticate(self, username, password, domain=None):
        return False

    def login(self, username, password, domain=None):
        if self.authenticate(username, password, domain):
            return True
        else:
            log.warning('Invalid login credentials for %s' % username)
            raise AccessDenied('Invalid login credentials')

    def _check_token(self, signature, token):
        cert = g.app.app_root.rstrip('/') + '/token.cert'
        try:
            self._token_sig = pki.verify(cert, signature, token)
        except ValueError as e:
            log.warning('Invalid Token: %s' % e)
            raise AccessDenied('Invalid Token')


    def parse_token(self, token):
        self._initial()
        token = if_unicode_to_bytes(token)
        signature, token = token.split(b'!!!!')
        self._token_sig = self._check_token(signature, token)
        self._token = js.loads(base64.b64decode(token))
        self._token_sig = signature
        utc_now = now()
        utc_expire = utc(self._token['expire'])
        if utc_now > utc_expire:
            raise AccessDenied('Token Expired')

    def scope_token(self, token, domain=None, tenant_id=None):
        self.parse_token(token)
        if 'user_id' in self._token:
            user_id = self._token['user_id']
        else:
            raise AccessDenied('user_id not in token')

        if 'username' in self._token:
            username = self._token['username']
        else:
            raise AccessDenied('username not in token')

        if 'roles' in self._token:
            roles = self._token['roles']
        else:
            raise AccessDenied('roles not in token')

        if 'expire' in self._token:
            expire = self._token['expire']
        else:
            raise AccessDenied('expire not in token')

        if 'domain' in self._token:
            if (self._token['domain'] is not None and
                    self._token['domain'] != domain):
                raise AccessDenied('token already scoped in domain')

        if 'tenant_id' in self._token:
            if (self._token['tenant_id'] is not None and
                    self._token['tenant_id'] != domain):
                raise AccessDenied('token already scoped in tenant')

        self.new_token(user_id, username,
                       domain, tenant_id,
                       expire=expire,
                       roles=roles)


    def _context_validate(self, context, value):
        if self.authenticated:
            token_context = self.token.get(context)
            if token_context is not None:
                if value is None:
                    raise AccessDenied("token not scoped for %s Global" %
                                       context)
                elif value == token_context:
                    setattr(self, '_' + context, value)
                else:
                    raise AccessDenied("token not scoped for %s '%s'" %
                                       (context,value,))
            else:
                    setattr(self, '_' + context, value)
        else:
            raise AccessDenied("not authenticated - access denied to %s '%s'" %
                               (context,value,))

    @property
    def user_id(self):
        if self.authenticated:
            return self.token['user_id']
        return None

    @property
    def username(self):
        if self.authenticated:
            return self.token['username']
        return None

    @property
    def expire(self):
        if self.authenticated:
            return self.token['expire']
        return None

    @property
    def created(self):
        if self.authenticated:
            return self.token['created']
        return None

    @property
    def roles(self):
        if self.authenticated:
            return to_tuple(self.token['roles'])
        return ()

    @property
    def domain(self):
        if self.authenticated:
            if self._domain is not None:
                return self._domain
            else:
                return self.token['domain']
        return None

    @domain.setter
    def domain(self, value):
        self._context_validate('domain', value)

    @property
    def tenant_id(self):
        if self.authenticated:
            if self._tenant_id is not None:
                return self._tenant_id
            else:
                return self.token['tenant_id']
        return None

    @tenant_id.setter
    def tenant_id(self, value):
        self._context_validate('tenant_id', value)
