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
import requests

from luxon import GetLogger
from luxon.utils.http import request
from luxon.utils.encoding import if_unicode_to_bytes
from luxon.exceptions import RestClientError, JSONDecodeError, NotFound
from luxon.structs.cidict import CiDict
from luxon import js
from luxon.core.endpoints import Endpoints
from luxon.utils.uri import clean_uri

log = GetLogger(__name__)

class RestClient(object):
    """HTTP Python Requests Wrapper.

    Provided for convienace to using RESTful API.

    Keeps connection to specfici host, port open and acts like a singleton
    providing each thread continues request apabilities without reconnecting.

    Args:
        uri (str): URI for RESTful API.
        timeout (float/tuple): How many seconds to wait for the server to send
            data before giving up, as a float, or a (connect timeout, read
            read timeout) tuple. Defaults to (2, 8) (optional)
        auth (tuple): Auth tuple to enable Basic/Digest/Custom HTTP Auth.
            ('username', 'password' ) pair.
        verify (str/bool): Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case
            it must be a path to a CA bundle to use. Defaults to True.
            (optional)
        cert (str/tuple): if String, path to ssl client cert file (.pem). If
            Tuple, ('cert', 'key') pair.
    """
    def __init__(self, uri, timeout=(2, 8),
                 auth=None, verify=True,
                 cert=None, default_region='default',
                 default_interface='public'):

        self.region = None
        self.interface = None
        self.uri = uri
        self.auth = auth
        self.timeout = timeout
        self.verify = verify
        self.cert = cert
        self.headers = CiDict()
        self.endpoints = Endpoints(default_region=default_region,
                                  default_interface=default_interface)
        try:
            self.collect_endpoints()
        except AttributeError:
            pass

    def execute(self, method, resource, data=None,
                headers={}, endpoint=None, region=None,
                interface=None, decode=True):
        """Execute Request.

        Args:
            method (str): method for the request.
                * GET - The GET method requests a representation of the
                  specified resource. Requests using GET should only
                  retrieve data.
                * POST - The POST method is used to submit an entity to the
                  specified resource, often causing a change in state or side
                  effects on the server
                * PUT - The PUT method replaces all current representations of
                  the target resource with the request payload.
                * PATCH - The PATCH method is used to apply partial
                  modifications to a resource.
                * DELETE - The DELETE method deletes the specified resource.
                * HEAD - The HEAD method asks for a response identical to
                  that of a GET request, but without the response body.
                * CONNECT - The CONNECT method establishes a tunnel to the
                  server identified by the target resource.
                * OPTIONS - The OPTIONS method is used to describe the
                  communication options for the target resource.
                * TRACE - The TRACE method performs a message loop-back test
                  along the path to the target resource.

            resource (str): Relative URI for the resource

            data (obj): str, dict or list to be converted to JSON.
                Otherwise sent as clear text. Objects with json method
                will be used to return json.

            headers (dict): HTTP Headers to send with the request.
            decode (bool): Decode response body as JSON where possible.

        Response body will be string unless json data is decoded either
        a list or dict will be returned.

        Returns tuple (status code, respone headers, response body)
        """
        headers = {**headers, **self.headers}

        if region is None:
            region = self.region

        if interface is None:
            interface = self.interface

        if endpoint is not None:
            uri = self.endpoints.get(endpoint, interface, region)
        else:
            try:
                uri = self.endpoints.get('tachyonic', interface, region)
            except NotFound:
                uri = self.uri

        resource = clean_uri("%s/%s" % (uri, resource))

        try:
            response = request(method, resource, data, headers,
                               self.auth, self.timeout, self.verify,
                               self.cert)

            if response.status_code >= 400:
                try:
                    json = response.json
                    title = json['error']['title']
                    description = json['error']['description']
                    raise RestClientError(response.status_code, description,
                                          title)
                except KeyError:
                    pass
                except JSONDecodeError:
                    pass

        except requests.ConnectionError as e:
            raise RestClientError('Connection error %s' % e, 'RestClient')
        except requests.HTTPError as e:
            raise RestClientError('HTTP error %s' % e, 'RestClient')
        except requests.ConnectTimeout as e:
            raise RestClientError('Connect timeout %s' % e, 'RestClient')
        except requests.ReadTimeout as e:
            raise RestClientError('Read timeout %s' % e, 'RestClient')
        except requests.Timeout as e:
            raise RestClientError('Timeout %s' % e, 'RestClient')

        return response
