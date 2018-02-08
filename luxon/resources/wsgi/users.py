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
from luxon.utils.password import hash


@register_resource('GET', '/v1/users', tag='role:root')
def users(req, resp):
    users = luxon_user(hide=('password',))
    users.sql_api()
    return users

@register_resource('GET', '/v1/user/{id}', tag='role:root')
def users(req, resp, id):
    users = luxon_user(model=dict, hide=('password',))
    users.sql_id(id)
    return users

@register_resource('POST', '/v1/user', tag='role:root')
def new_user(req, resp):
    user = luxon_user(model=dict, hide=('password',))
    user = req.json.copy()
    user['tag'] = 'tachyonic'
    if 'password' in user and user['password'] is not None:
        user['password'] = hash(user['password'])
    user.update(user)
    user.commit()
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
