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
from luxon.api.restclient import RestClient
from luxon.utils.cache import memoize

class Client(RestClient):
    """Tachyonic RestApi Client.

    Client wrapped around RestClient using python requests.

    Provided for convienace to using RESTful API.

    Provides simple authentication methods and tracks endpoints.
    Keeps connection to specfici host, port open and acts like a singleton
    providing each thread continues request apabilities without reconnecting.

    Args:
        url (str): URL of Tachyonic main endpoint API.
        endpoint (str): Default End point to use for all calls. (optional)
        timeout (float/tuple): How many seconds to wait for the server to send
            data before giving up, as a float, or a (connect timeout, read
            read timeout) tuple. Defaults to (8, 2) (optional)
        auth (tuple): Auth tuple to enable Basic/Digest/Custom HTTP Auth.
            ('username', 'password' ) pair.
        verify (str/bool): Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case
            it must be a path to a CA bundle to use. Defaults to True.
            (optional)
        cert (str/tuple): if String, path to ssl client cert file (.pem). If
            Tuple, ('cert', 'key') pair.
    """
    @memoize(120)
    def collect_endpoints(self):
        response = super().execute('GET', '/v1/endpoints')
        for endpoint in response.json:
            self.endpoints.set(endpoint['name'], endpoint['interface'],
                               endpoint['region'], endpoint['uri'])

    def authenticate(self, username, password, domain='default'):
        """Authenticate using credentials.

        Once authenticated execute will be processed using the context
        relative to user credentials.

        Args:
            username (str): Username.
            password (str): Password.
            domain (str): Name of domain for context.

        Returns authenticated result.
        """
        auth_url = "/v1/token"

        if 'X-Tenant-Id' in self.headers:
            del self.headers['X-Tenant-Id']
        if 'X-Auth-Token' in self.headers:
            del self.headers['X-Auth-Token']

        data = {}
        data['username'] = username
        data['password'] = password
        data['domain'] = domain

        response = self.execute("POST", auth_url, data)

        if 'token' in response.json:
            self.headers['X-Auth-Token'] = response.json['token']
            self.auth_token = response.json['token']

        return response

    def token(self, token):
        """Authenticate using Token.

        Once authenticated execute will be processed using the context
        relative to user credentials.

        Args:
            token (str): Token Key.
            domain (str): Name of domain for context.
            tenant_id (str): Tenant id for context. (optional)

        Returns authenticated result.
        """
        auth_url = "/v1/token"

        response = self.execute("GET", auth_url)

        if 'token' in response.json:
            self.headers['X-Auth-Token'] = response.json['token']
        if 'tenant_id' in response.json:
            self.headers['X-Tenant-Id'] = response.json['tenant_id']
        if 'domain' in response.json:
            self.headers['X-Domain'] = response.json['domain']

        return response

    def scope(self, domain, tenant_id=None):
        """Scope Token.
        """
        auth_url = "/v1/token"

        self.headers['X-Domain'] = domain
        if tenant_id is not None:
            self.headers['X-Tenant-Id'] = tenant_id
        elif 'X-Tenant-Id' in self.headers:
            del self.headers['X-Tenant-Id']

        scope = {}
        scope['domain'] = domain
        scope['tenant_id'] = tenant_id

        response = self.execute("PATCH", auth_url, scope)

        if 'token' in response.json:
            self.headers['X-Auth-Token'] = response.json['token']
        if 'tenant_id' in response.json:
            self.headers['X-Tenant-Id'] = response.json['tenant_id']
        if 'domain' in response.json:
            self.headers['X-Domain'] = response.json['domain']

        return response

    def set_context(self, auth_token, scope_token, domain, tenant_id):

        if 'X-Domain' in self.headers:
            del self.headers['X-Domain']
        if 'X-Tenant-Id' in self.headers:
            del self.headers['X-Tenant-Id']

        if auth_token is not None:
            self.auth_token = auth_token
            self.headers['X-Auth-Token'] = self.auth_token

        if scope_token is not None:
            self.headers['X-Auth-Token'] = scope_token

        if domain is not None:
            self.headers['X-Domain'] = domain

        if tenant_id is not None:
            self.headers['X-Tenant-Id'] = tenant_id

    def unscope(self):
        """Unscope Token.
        """
        self.headers['X-Auth-Token'] = self.auth_token
        if 'X-Domain' in self.headers:
            del self.headers['X-Domain']
        if 'X-Tenant-Id' in self.headers:
            del self.headers['X-Tenant-Id']

    def new_endpoint(self, name, interface, region, uri):
        req = {}
        req['name'] = name
        req['interface'] = interface
        req['region'] = region
        req['uri'] = uri
        return self.execute('POST', '/v1/endpoint', req)

    def list_endpoints(self):
        return self.execute('GET', '/v1/endpoints')

    def delete_endpoint(self, id):
        return self.execute('DELETE', '/v1/endpoint/%s' % id)

    def user_domains(self):
        return self.execute('GET', '/v1/domains')

    def user_tenants(self):
        return self.execute('GET', '/v1/tenants')
