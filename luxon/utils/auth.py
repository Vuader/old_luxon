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
from luxon.utils.password import valid as is_valid_password

def user_roles(user_id, domain=None, tenant_id=None):
    roles = []
    with db() as conn:
        values = []
        values.append(user_id)
        query = 'SELECT' + \
                ' luxon_user_role.id as assignment_id,' + \
                ' luxon_user_role.role_id AS role_id,' + \
                ' luxon_user_role.domain_id as domain_id,' + \
                ' luxon_role.name as role,' + \
                ' luxon_user_role.tenant_id as tenant_id FROM' + \
                ' luxon_user_role LEFT JOIN luxon_role ON' + \
                ' luxon_user_role.role_id = luxon_role.id' + \
                ' LEFT JOIN luxon_domain ON' + \
                ' luxon_user_role.domain_id = luxon_domain.id' + \
                ' OR luxon_user_role.domain_id is NULL' + \
                ' LEFT JOIN luxon_tenant ON' + \
                ' luxon_user_role.tenant_id = luxon_tenant.id' + \
                ' OR luxon_user_role.tenant_id is NULL' + \
                ' where luxon_user_role.user_id = %s'
        if domain is not None:
            query += ' and luxon_domain.name = %s'
            values.append(domain)
        else:
            query += ' and luxon_user_role.domain_id IS NULL'

        if tenant_id is not None:
            query += ' and luxon_user_role.tenant_id = %s'
            values.append(tenant_id)
        else:
            query += ' and luxon_user_role.tenant_id IS NULL'

        crsr = conn.execute(query, values)

        for role in crsr:
            roles.append(role['role'])

    return roles

def authorize(tag, username=None, password=None, domain=None):
    with db() as conn:
        auth = {}
        crsr = conn.execute('SELECT luxon_user.id AS user_id' +
                            ' ,luxon_user.last_login AS last_login' +
                            ' ,luxon_user.username AS username' +
                            ' ,luxon_user.password AS password' +
                            ' ,luxon_domain.name AS domain' +
                            ' FROM luxon_user' +
                            ' LEFT JOIN luxon_domain' +
                            ' ON luxon_user.domain_id = luxon_domain.id' +
                            ' WHERE luxon_user.enabled = 1' +
                            ' AND luxon_user.username = %s' +
                            ' AND luxon_domain.name = %s' +
                            ' AND luxon_user.tag = %s',
                            (username, domain, tag))
        result = crsr.fetchone()
        if result is not None:
            # Validate Password againts stored HASHED Value.
            if is_valid_password(password, result['password']):
                auth = result.copy()
                return (True, auth,)

        return (False, auth,)

def domain_id(domain):
    if domain is not None:
        with db() as conn:
            crsr = conn.execute('SELECT * FROM luxon_domain WHERE name = %s',
                                domain)
            result = crsr.fetchone()
            if result is not None:
                return result['id']
    return None
