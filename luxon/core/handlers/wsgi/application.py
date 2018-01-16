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

from luxon.core.application import ApplicationBase
from luxon.core.handlers.wsgi.request import Request
from luxon.core.handlers.wsgi.response import Response
from luxon.exceptions import NotFound, AccessDenied

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
        if isinstance(exception, AccessDenied):
            resp.status = 403
        elif isinstance(exception, NotFound):
            resp.status = 404

        try:
            resp.status = exception.status
        except AttributeError:
            pass

        return str(exception)
