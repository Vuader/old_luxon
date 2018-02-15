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
from luxon import register_resource
from luxon.constants import TEXT_HTML
from luxon import g

@register_resource('POST', '/login')
def login(req, resp):
    resp.content_type = TEXT_HTML
    username = req.get_first('username')
    password = req.get_first('password')
    domain = req.get_first('domain')
    req.token.authenticate(username,
                           password,
                           domain)
    req.session['token'] = req.token.encoded
    req.session.save()
    resp.redirect('/')

@register_resource('GET', '/logout')
def logout(req, resp):
    resp.content_type = TEXT_HTML
    req.session.clear()
    req.session.save()
    req.token.clear()
    resp.redirect('/')

@register_resource('POST', '/scope')
def scope(req, resp):
    resp.content_type = TEXT_HTML
    x_domain = req.get_first('X-Domain')
    x_tenant_id = req.get_first('X-Tenant-Id')
    if x_domain is not None:
        scoped = g.client.scope(x_domain, x_tenant_id)
        scoped = scoped['token']
        req.session['scoped'] = scoped
        req.session['domain'] = x_domain
        req.session['tenant_id'] = x_tenant_id
    else:
        req.session['scoped'] = None
        req.session['domain'] = None
        req.session['tenant_id'] = None

    req.session.save()
    resp.redirect('/')
