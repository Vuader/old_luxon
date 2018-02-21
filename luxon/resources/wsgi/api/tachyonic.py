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
from luxon import db
from luxon import GetLogger
from luxon.exceptions import AccessDenied
from luxon.utils.imports import get_class
from luxon import register_resources
from luxon import register_resource
from luxon.models.endpoints import luxon_endpoint
from luxon.models.users import luxon_user, luxon_tenant
from luxon.utils.password import hash
from luxon.utils.auth import user_domains, user_tenants

log = GetLogger(__name__)


@register_resource('GET', '/v1/rbac/domains')
def domains(req, resp):
    search = req.query_params.get('term')
    domains_list = user_domains(req.token.user_id)
    if search is not None:
        filtered = []
        for domain in domains_list:
            if search in domain:
                filtered.append(domain)
        return filtered
    return domains_list

@register_resource('GET', '/v1/tenants', tag='admin')
def tenants(req, resp):
    tenants = luxon_tenant()
    tenants.sql_api()
    return tenants

@register_resource('POST', '/v1/tenant', tag='admin')
def new_tenant(req, resp):
    tenant = luxon_tenant(model=dict)
    tenant.update(req.json)
    tenant.commit()
    return tenant

@register_resource([ 'PUT', 'PATCH' ], '/v1/tenant/{id}', tag='admin')
def update_tenant(req, resp, id):
    tenant = luxon_tenant(model=dict)
    tenant.sql_id(id)
    tenant.update(req.json)
    tenant.commit()
    return tenant

@register_resource('GET', '/v1/tenant/{id}', tag='admin')
def view_tenant(req, resp, id):
    tenant = luxon_tenant(model=dict)
    tenant.sql_id(id)
    return tenant

@register_resource('DELETE', '/v1/tenant/{id}', tag='admin')
def delete_tenant(req, resp, id):
    tenant = luxon_tenant(model=dict)
    tenant.sql_id(id)
    tenant.delete()

@register_resource('GET', '/v1/regions')
def regions(req, resp):
    regions = []
    with db() as conn:
        crsr = conn.execute('SELECT region FROM luxon_endpoint GROUP BY region')
        for region in crsr:
            regions.append(region['region'])
    resp.set_cache_max_age(120)
    return regions

@register_resource('GET', '/v1/endpoints')
def endpoints(req, resp):
    endpoints = luxon_endpoint()
    endpoints.sql_api()
    resp.set_cache_max_age(120)
    return endpoints

@register_resource('POST', '/v1/endpoint', tag='role:root')
def new_endpoint(req, resp):
    endpoint = luxon_endpoint(model=dict)
    endpoint.update(req.json)
    endpoint.commit()
    return endpoint

@register_resource([ 'PUT', 'PATCH' ], '/v1/endpoint/{id}', tag='role:root')
def update_endpoint(req, resp, id):
    endpoint = luxon_endpoint(model=dict)
    endpoint.sql_id(id)
    endpoint.update(req.json)
    endpoint.commit()
    return endpoint

@register_resource('GET', '/v1/endpoint/{id}', tag='role:root')
def view_endpoint(req, resp, id):
    endpoint = luxon_endpoint(model=dict)
    endpoint.sql_id(id)
    return endpoint

@register_resource('DELETE', '/v1/endpoint/{id}', tag='role:root')
def delete_endpoint(req, resp, id):
    with db() as conn:
        conn.execute('DELETE FROM luxon_endpoint WHERE id = %s',
                    id)
        conn.commit()

@register_resources()
class Token(object):
    """Token Middleware.

    Validates token and sets request.token object.

    Luxon tokens use PKI. Its required to have the private key to sign
    new tokens on the tachyonic api. Endpoints will require the public cert
    to validate tokens authenticity.

    The tokens should be stored in the application root. Usually where the wsgi
    file is located.

    Creating token:
        openssl req  -nodes -new -x509  -keyout token.key -out token.cert
    """
    def __init__(self):
        g.router.add('GET', '/v1/token', self.get)
        g.router.add('POST', '/v1/token', self.post)
        g.router.add('PATCH', '/v1/token', self.patch, tag='login')

    def get(self, req, resp):
        return req.token

    def post(self, req, resp):
        request_object = req.json
        req.token.login(request_object.get('username',
                                           None),
                    request_object.get('password', None),
                    request_object.get('domain', None))
        return req.token

    def patch(self, req, resp):
        request_object = req.json
        req.token.scope_token(req.token.token['token'],
                              request_object.get('domain'),
                              request_object.get('tenant_id'))
        return req.token


@register_resource('GET', '/v1/users', tag='role:root')
def users(req, resp):
    users = luxon_user(hide=('password',))
    users.sql_api()
    return users

@register_resource('GET', '/v1/user/{id}', tag='role:root')
def user(req, resp, id):
    users = luxon_user(model=dict, hide=('password',))
    users.sql_id(id)
    return users

@register_resource('POST', '/v1/user', tag='role:root')
def new_user(req, resp):
    model_user = luxon_user(model=dict, hide=('password',))
    user = req.json.copy()
    user['tag'] = 'tachyonic'
    if 'password' in user and user['password'] is not None:
        user['password'] = hash(user['password'])
    model_user.update(user)
    model_user.commit()
    return user

@register_resource([ 'PUT', 'PATCH' ], '/v1/user/{id}', tag='role:root')
def update_user(req, resp, id):
    user = luxon_user(model=dict, hide=('password',))
    user.sql_id(id)
    user = req.json.copy()
    user['tag'] = 'tachyonic'
    if 'password' in user and user['password'] is not None:
        user['password'] = hash(user['password'])
    user.update(user)
    user.commit()
    return user

@register_resource('DELETE', '/v1/user/{id}', tag='role:root')
def delete_user(req, resp, id):
    user = luxon_user(model=dict, hide=('password',))
    user.sql_id(id)
    user.delete()
