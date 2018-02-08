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
from luxon.core.application import ApplicationBase
from luxon.core.handlers.wsgi.request import Request
from luxon.core.handlers.wsgi.response import Response
from luxon.exceptions import (Error, NotFound,
                              AccessDenied, JSONDecodeError,
                              ValidationError, FieldError)
from luxon.constants import HTTP_STATUS_CODES
from luxon.structs.htmldoc import HTMLDoc
from luxon import render_template
from luxon import GetLogger

log = GetLogger(__name__)

class Application(ApplicationBase):
    """This class is part of the main entry point into the application.

    Each instance provides a callable interface for WSGI requests.

    Args:
        name (str): Unique Name for application. Use __name__ of module to
            ensure root path for application can be found conveniantly.

    Keyword Arguments:
        app_root (str): Path to application root. (e.g. The location of
            'settings.ini', 'policy.json' and overiding 'templates')

    Attributes:
        name (str): Application name used.
        app_root (str): Application root path used.
        context: Application context for process.
        modules (dict): Dictionary with modules and references imported.
    """
    _REQUEST_CLASS = Request
    _RESPONSE_CLASS = Response

    def handle_error(self, req, resp, exception, traceback):
        title = None
        description = None

        try:
            resp.status = exception.status
        except AttributeError:
            if isinstance(exception, AccessDenied):
                resp.status = 403
            elif isinstance(exception, NotFound):
                resp.status = 404
            elif isinstance(exception, JSONDecodeError):
                resp.status = 400
            elif isinstance(exception, FieldError):
                resp.status = 400
            elif isinstance(exception, ValidationError):
                resp.status = 400
            else:
                resp.status = 500

        if isinstance(exception, FieldError):
            description = str(exception)

        if title is None:
            try:
                title = exception.title
            except AttributeError:
                if resp.status in HTTP_STATUS_CODES:
                    title = str(resp.status) + ' ' +  HTTP_STATUS_CODES[resp.status]
                else:
                    title = exception.__class__.__name__

        if description is None:
            try:
                description = exception.description
            except AttributeError:
                description = str(exception)

        try:
            for header in exception.headers:
                resp.set_header(header, exception.headers[header])
        except AttributeError:
            pass

        if 'error_template' in g:
            return render_template(g, title, description)
        elif resp.content_type is None or 'json' in resp.content_type.lower():
            to_return = {}
            to_return['error'] = {}
            to_return['error']['title'] = title
            to_return['error']['description'] = description

            return to_return

        elif 'html' in resp.content_type.lower():
            dom = HTMLDoc()
            html = dom.create_element('html')
            head = html.create_element('head')
            t = head.create_element('title')
            t.append(resp.status)
            body = html.create_element('body')
            h1 = body.create_element('h1')
            h1.append(title)
            h2 = body.create_element('h2')
            h2.append(description)
            return dom.get()
        else:
            return title + ' ' + description
