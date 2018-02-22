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
from luxon import g
from luxon import db
from luxon import GetLogger
from luxon import register_resource
from luxon.models.tenants import luxon_tenant

log = GetLogger(__name__)

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
