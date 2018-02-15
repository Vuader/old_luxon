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
import traceback

from luxon import g
from luxon.core.logger import GetLogger
from luxon.core.globals import Globals
from luxon.core.config import Config
from luxon.core.request import RequestBase
from luxon.core.response import ResponseBase
from luxon.exceptions import (Error,
                              NotFound,
                              HTTPError,
                              AccessDenied,
                              NoContextError,)
from luxon.utils import imports
from luxon.utils.timer import Timer
from luxon.utils.objects import object_name

log = GetLogger()

def determine_app_root(name, app_root=None):
    if app_root is None:
        if name == "__main__" or "_mod_wsgi" in name:
            app_mod = imports.import_module(name)
            return os.path.abspath( \
                os.path.dirname( \
                    app_mod.__file__)).rstrip('/')
        else:
            log.error("Unable to determine application root." +
                      " Using current working directory '%s'" % os.getcwd())
            return os.getcwd().rstrip('/')
    else:
        if os.path.exists(app_root) and not os.path.isfile(app_root):
            return app_root.rstrip('/')
        else:
            raise Error("Invalid path for root '%s'" % app_root)

def load_config(ini):
    config = Config()
    if os.path.isfile(ini):
        config.load(ini)
        return config
    log.warning("%s not found" % ini)

    return config

class ApplicationBase(object):
    """This base class is part of the main entry point into the application.

    Each instance provides a callable interface for requests.

    Args:
        name (str): Unique Name for application. Use __name__ of module to
            ensure root path for application can be found conveniantly.

    Keyword Arguments:
        app_root (str): Path to application root. (e.g. The location of
            'settings.ini', 'policy.json' and overiding 'templates')

    Attributes:
        name (str): Application name used.
        app_root (str): Application root path used.
    """
    _REQUEST_CLASS = RequestBase
    _RESPONSE_CLASS = ResponseBase

    __slots__ = ('app_root',
                'name',
                'active_resources',
                'config',
                '_policy_compiled_rules',
                '_route',
                'modules',
                'middleware',)

    def __init__(self, name, app_root=None, ini=None, content_type=None):
        try:
            with Timer() as elapsed:
                # Set current app as global
                g.app = self

                # Attempt to determine application root.
                g.app_root = self.app_root = app_root = determine_app_root(name,
                                                                       app_root)

                # Set Application Name
                self.name = name

                # Load Configuration
                if ini is None:
                    g.config = self.config = load_config(self.app_root +
                                                         '/settings.ini')
                else:
                    g.config = self.config = load_config(ini)

                # Configure Logger.
                GetLogger().app_configure()

                if content_type is not None:
                    self._RESPONSE_CLASS._DEFAULT_CONTENT_TYPE = content_type

                # Started Application
                log.info('Started Application'
                          ' %s' % name +
                          ' app_root: %s' % app_root,
                          timer=elapsed())

        except Exception:
            trace = str(traceback.format_exc())
            log.critical("%s" % trace)
            raise

    def __call__(self, *args, **kwargs):
        """Application Request Interface.

        A clean request and response object is provided to the interface that
        is unique this to this thread.

        It passes any args and kwargs to the interface.

        Response object is returned.
        """
        try:
            with Timer() as elapsed:
                # Request Object.
                request = g.current_request = self._REQUEST_CLASS(*args,
                                                                  **kwargs)

                # Response Object.
                response = self._RESPONSE_CLASS(*args,
                                                **kwargs)

                # Set Response object for request.
                request.response = response

                # Process the middleware 'pre' method before routing it
                for middleware in g.middleware_pre:
                    middleware(request, response)

                # Route Object.
                resource, method, r_kwargs, target, tag = g.router.find( \
                    request.method, \
                    request.route)

                # Route Kwargs in requests.
                request.route_kwargs = r_kwargs

                # Set route tag in requests.
                request.tag = tag

                # Execute Routed View.
                try:
                    # Run View method.
                    if resource is not None:
                        # Process the middleware 'resource' after routing it
                        for middleware in g.middleware_resource:
                            middleware(request, response)
                        view = resource(request,
                                        response,
                                        **r_kwargs)
                        if view is not None:
                            response.body(view)
                    else:
                        raise NotFound('Route not found' +
                                       " Method '%s'" % request.method +
                                       " Route '%s'" % request.route)
                finally:
                    # Process the middleware 'post' at the end
                    for middleware in g.middleware_post:
                        middleware(request, response)
            # Return response object.
            return response

        except HTTPError as exception:
            trace = str(traceback.format_exc())
            if log.debug_mode():
                log.debug('%s' % (trace))
            else:
                log.info('%s: %s' % (object_name(exception),
                                     exception))
            self._proxy_handle_error(request, response, exception, trace)
            # Return response object.
            return response
        except Error as exception:
            trace = str(traceback.format_exc())
            if log.debug_mode():
                log.debug('%s' % (trace))
            else:
                log.error('%s: %s' % (object_name(exception),
                                      exception))
            self._proxy_handle_error(request, response, exception, trace)
            # Return response object.
            return response
        except Exception as exception:
            trace = str(traceback.format_exc())
            if log.debug_mode():
                log.debug('%s' % (trace))
            else:
                log.error('%s: %s' % (object_name(exception),
                                      exception))
            self._proxy_handle_error(request, response, exception, trace)
            # Return response object.
            return response
        finally:
            # Completed Request
            log.info('Completed Request',
                      timer=elapsed())

    def _proxy_handle_error(self, request, response, exception, traceback):
        if hasattr(self, 'handle_error'):
            view = self.handle_error(request, response, exception, traceback)
            if view is not None:
                response.body(view)
        else:
            raise
