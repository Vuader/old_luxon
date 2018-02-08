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
import re
import cgi
import string
import requests
from collections import OrderedDict

from luxon import js
from luxon import __identity__
from luxon import GetLogger
from luxon.utils.timer import Timer
from luxon.utils.uri import host_from_uri
from luxon.exceptions import RestClientError
from luxon.constants import HTTP_STATUS_CODES
from luxon.structs.threaddict import ThreadDict
from luxon.utils.encoding import if_unicode_to_bytes
from luxon.utils.cache import Cache
from luxon.exceptions import JSONDecodeError
from luxon.utils.strings import unquote_string

log = GetLogger(__name__)


class ForwardedElement(object):
    """Representation of Forwarded header.

    Reference to RFC 7239, Section 4.

    Attributes:
        src (str): The value of the 'for' parameter or if the
            parameter is absent None. Identifies the node
            making the request to the proxy.
        by (str): The value of the 'by' parameter or if the
            the parameter is absent None. Identifies the
            client-facing interface of the proxy.
        host (str): The value of the 'host' parameter or if
            the parameter is absent None. Provides the host
            request header field as received by the proxy.
        proto (str): The value of the 'proto' parameter or
            if the parameter is absent None. Indicates the
            protocol that was used to make the request to
            the proxy.
    """

    __slots__ = ('src', 'by', 'host', 'proto')

    def __init__(self):
        self.src = None
        self.by = None
        self.host = None
        self.proto = None


def parse_forwarded_header(forwarded):
    """Parses the value of a Forwarded header.

    Parse Forwarded headers as specified by RFC 7239:

        * Check that every value has valid syntax in general.
        * Un-escapes found escape sequences.

    Arguments:
        forwarded (str): Value of a Forwarded header

    Returns:
        list: Sequence of ForwardedElement instances.
    """
    tchar = string.digits + string.ascii_letters + r"!#$%&'*+.^_`|~-"

    token = r'[{tchar}]+'.format(tchar=tchar)

    qdtext = r'[{0}]'.format(
        r''.join(chr(c) for c in (0x09, 0x20, 0x21) + tuple(range(0x23, 0x7F))))

    quoted_pair = r'\\[\t !-~]'

    quoted_string = r'"(?:{quoted_pair}|{qdtext})*"'.format(
        qdtext=qdtext, quoted_pair=quoted_pair)

    forwarded_pair = (
        r'({token})=({token}|{quoted_string})'.format(
            token=token,
            quoted_string=quoted_string))

    forwarded_pair_re = re.compile(forwarded_pair)

    elements = []

    pos = 0
    end = len(forwarded)
    need_separator = False
    parsed_element = None

    while 0 <= pos < end:
        match = forwarded_pair_re.match(forwarded, pos)

        if match is not None:
            if need_separator:
                pos = forwarded.find(',', pos)
            else:
                pos += len(match.group(0))
                need_separator = True

                name, value = match.groups()

                # Reference to RFC 7239.
                # Forwarded parameter names are
                # not case sensitive.
                name = name.lower()

                if value[0] == '"':
                    value = unquote_string(value)
                if not parsed_element:
                    parsed_element = ForwardedElement()
                if name == 'by':
                    parsed_element.by = value
                elif name == 'for':
                    parsed_element.src = value
                elif name == 'host':
                    parsed_element.host = value
                elif name == 'proto':
                    # RFC 7239 only requires that 'proto' value
                    # HOST ABNF described in RFC 7230.
                    parsed_element.proto = value.lower()
        elif forwarded[pos] == ',':
            need_separator = False
            pos += 1

            if parsed_element:
                elements.append(parsed_element)
                parsed_element = None

        elif forwarded[pos] == ';':
            need_separator = False
            pos += 1

        elif forwarded[pos] in ' \t':
            # Allow whitespace even between forwarded-pairs.
            # This however is not permitted in RFC 7239 doesn't.
            pos += 1

        else:
            pos = forwarded.find(',', pos)

    if parsed_element:
        elements.append(parsed_element)

    return elements


def content_type_encoding(header):
    """Gets the encoding from Content-Type header.

    Args:
        header (str): Content-Type header value.
    """

    if not header:
        return None

    content_type, params = cgi.parse_header(header)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'

    return None


CACHE_CONTROL_RE = re.compile(r"[a-z_\-]+=[0-9]+", re.IGNORECASE)
CACHE_CONTROL_OPTION_RE = re.compile(r"[a-z_\-] +", re.IGNORECASE)


class CacheControl(object):
    def __init__(self):
        self.must_revalidate = None
        self.no_cache = False
        self.no_store = False
        self.no_transform = False
        self.public = False
        self.private = False
        self.proxy_revalidate = False
        self.max_age = None
        self.s_maxage = None


def parse_cache_control_header(header):
    values = {'options': []}
    cachecontrol = CacheControl()

    CACHE_CONTROL_OPTION_RE.findall(header)
    for option in CACHE_CONTROL_OPTION_RE.findall(header):
        option = option.replace('-', '_').lower()

    CACHE_CONTROL_RE.findall(header)
    for option in CACHE_CONTROL_RE.findall(header):
        option, value = option.split('=')
        option = option.replace('-', '_').lower()
        setattr(cachecontrol, option, value)

    return cachecontrol


sessions = ThreadDict()


def _debug(method, url, payload, request_headers, response_headers,
           response, status_code, elapsed):
    if log.debug_mode():
        log.debug('Method: %s' % method +
                  ', URL: %s' % url +
                  ' (%s %s)' % (status_code, HTTP_STATUS_CODES[status_code]),
                  timer=elapsed)
        for header in request_headers:
            log.debug('Request Header: %s="%s"' % (header,
                                                   request_headers[header]))
        for header in response_headers:
            log.debug('Response Header: %s="%s"' % (header,
                                                    response_headers[header]))
        log.debug(payload, prepend='Requet Payload')
        log.debug(response, prepend='Response Payload')


class Response(object):
    __slots__ = '_result'

    def __init__(self, requests_result):
        self._result = requests_result

    @property
    def body(self):
        return self._result.content

    @property
    def headers(self):
        return self._result.headers

    @property
    def status_code(self):
        return self._result.status_code

    def __len__(self):
        return len(self.body)

    @property
    def content_type(self):
        try:
            header = self.headers['content-type']
            content_type, params = cgi.parse_header(header)
            if content_type is not None:
                return str(content_type).upper()
            else:
                return None
        except KeyError:
            return None

    @property
    def json(self):
        content_type = self.content_type
        if (content_type is not None and
                'JSON' in content_type):

            if self.encoding != 'UTF-8':
                raise RestClientError('JSON requires UTF-8 Encoding')

            try:
                if self.status_code != 204:
                    return js.loads(self.body)
                else:
                    return b''

            except JSONDecodeError as e:
                raise RestClientError('JSON Decode: %s' % e)

    @property
    def encoding(self):
        try:
            header = self.headers['content_type']
            content_type, params = cgi.parse_header(header)
            if 'charset' in params:
                return params['charset'].strip("'\"").upper()
            if 'text' in content_type:
                return 'ISO-8859-1'
        except KeyError:
            pass

        return self._result.encoding.upper()


def request(method, uri, data,
            headers={}, auth=None,
            timeout=(2, 8), verify=True,
            cert=None):
    with Timer() as elapsed:
        method = method.upper()
        cache = Cache()

        if data is not None:
            if hasattr(data, 'json'):
                data = data.json
            elif isinstance(data, (dict, list, OrderedDict)):
                data = js.dumps(data)

        data = if_unicode_to_bytes(data)

        host = host_from_uri(uri)

        cache_obj = str(method) + str(uri) + str(data)
        cached = cache.load(cache_obj)
        if cached is not None:
            return Response(cached)

        try:
            session = sessions[host]
            log.debug("Using exisiting session: '%s'" % host)
        except KeyError:
            session = sessions[host] = requests.Session()

        if data is None:
            data = ''

        headers['User-Agent'] = __identity__
        headers['Content-Length'] = str(len(data))

        request = requests.Request(method,
                                   uri,
                                   data=data,
                                   headers=headers,
                                   auth=auth)

        session_request = session.prepare_request(request)

        response = session.send(session_request,
                                timeout=timeout,
                                verify=verify,
                                cert=cert)

        _debug(method, uri, data, headers, response.headers,
               response.content, response.status_code, elapsed())

        if 'Cache-Control' in response.headers:
            cache_control = parse_cache_control_header(
                response.headers['cache-control'])
            if cache_control.max_age is not None:
                cache.store(cache_obj, response, int(cache_control.max_age))
        return Response(response)
