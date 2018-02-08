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
from luxon import db
from luxon import register_resource

from luxon.models.users import luxon_user

@register_resource('GET', '/v1/users', tag='role:root')
def users(req, resp):
    endpoints = luxon_user(hide=('password',))
    endpoints.sql_query("SELECT * FROM luxon.user")
    return endpoints
"""
@register_resource('POST', '/v1/endpoint', tag='role:root')
def new_endpoint(req, resp):
    endpoint = model_endpoint(model=dict)
    endpoint.update(req.json)
    endpoint.commit()
    return endpoint

@register_resource([ 'PUT', 'PATCH' ], '/v1/endpoint/{id}', tag='role:root')
def update_endpoint(req, resp, id):
    endpoint = model_endpoint(model=dict)
    endpoint.sql_id(id)
    endpoint.update(req.json)
    endpoint.commit()
    return endpoint

@register_resource('DELETE', '/v1/endpoint/{id}', tag='role:root')
def delete_endpoint(req, resp, id):
    with db() as conn:
        conn.execute('DELETE FROM endpoint WHERE id = %s',
                    id)
        conn.commit()
"""
