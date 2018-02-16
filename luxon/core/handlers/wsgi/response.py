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
from http.cookies import SimpleCookie, CookieError

from luxon import __identity__
from luxon.core.response import ResponseBase
from luxon import constants as const
from luxon.utils.encoding import is_ascii
from luxon.utils.timezone import TimezoneGMT
from luxon.utils.http import http_see_other
from luxon.structs.cidict import CiDict


GMT_TIMEZONE = TimezoneGMT()

class Response(ResponseBase):
    """Represents an HTTP response to a client request.

    Args:
        env (dict): A WSGI environment dict passed in from the server.
            As per PEP-3333.
        start_response (function): callback function supplied by the server
            which takes the HTTP status and headers as arguments.

    Attributes:
        status (int): HTTP status code. (e.g. '200') Default 200.
    """
    _DEFAULT_CONTENT_TYPE = const.APPLICATION_JSON
    _BODILESS_STATUS_CODES = (
        100,
        101,
        204,
        304,
    )

    __slots__ = (
        '_headers',
        '_http_response_status_code',
        '_cookies',
        '_start_response',
    )

    def __init__(self, environ, start_response):
        super().__init__(environ, start_response)
        self._start_response = start_response

        # Used internally.
        self._http_response_status_code = 200

        # Some Default Headers..
        self._headers['X-Powered-By'] = __identity__

        self._cookies = None

    @property
    def status(self):
        return self._http_response_status_code

    @status.setter
    def status(self, value):
        self._http_response_status_code = value

    def redirect(self, uri):
        http_see_other(uri)

    def set_header(self, name, value):
        """Set a header for this response to a given value.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
            value (str): Value for the header.
        """

        name = str(name)
        value = str(value)

        self._headers[name.title()] = value

    def set_cache_max_age(self, seconds):
        self.set_header('Cache-Control', 'max-age=%s' % seconds)

    def delete_header(self, name):
        """Delete a header that was previously set for this response.

        If the header was not previously set, nothing is done (no error is
        raised).

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
        """

        self._headers.pop(name.title(), None)

    def append_header(self, name, value):
        """Set or append a header for this response.

        If the header already exists, the new value will be appended
        to it, delimited by a comma. Some header specifications support
        this format, Set-Cookie being the notable exceptions.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
            value (str): Value for the header.
        """
        name = str(name)
        value = str(value)

        name = name.title()
        if name in self._headers:
            value = self._headers[name] + ',' + value

        self._headers[name] = value

    def set_headers(self, headers):
        """Set several headers at once.

        Calling this method overwrites existing values, if any.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            headers (dict or list): A dictionary of header names and values
                to set, or a 'list' of (*name*, *value*) tuples.

        Raises:
            ValueError: `headers` was not a 'dict' or 'list' of 'tuple'.
        """

        if isinstance(headers, (dict, CiDict,)):
            headers = headers.items()

        _headers = self._headers

        for name, value in headers:
            name = str(name)
            value = str(value)

            _headers[name.title()] = value

    def get_header(self, name):
        """Retrieve the raw string value for the given header.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).

        Returns:
            str: The header's value if set, otherwise None.
        """
        return self._headers.get(name.title(), None)

    def set_cookie(self, name, value, expires=None, max_age=None,
                   domain=None, path=None, secure=False, http_only=True):
        """Set a response cookie.

        This method can be called multiple times to add one or
        more cookies to the response.

        Args:
            name (str): Cookie name
            value (str): Cookie value

        Keyword Args:
            expires (datetime): Specifies when the cookie should expire.
                By default, cookies expire when the user agent exits.

                Refer to RFC 6265, Section 4.1.2.1

            max_age (int): Defines the lifetime of the cookie in
                seconds. By default, cookies expire when the user agent
                exits. If both 'max_age' and 'expires' are set, the
                latter is ignored by the user agent.

                Refer to RFC 6265, Section 4.1.2.2

            domain (str): Restricts the cookie to a specific domain and
                any subdomains of that domain. By default, the user
                agent will return the cookie only to the origin server.
                When overriding this default behavior, the specified
                domain must include the origin server. Otherwise, the
                user agent will reject the cookie.

                Refer to RFC 6265, Section 4.1.2.3

            path (str): Scopes the cookie to the given path plus any
                subdirectories under that path (the "/" character is
                interpreted as a directory separator). If the cookie
                does not specify a path, the user agent defaults to the
                path component of the requested URI.

                User agent interfaces do not always isolate cookies by
                path and so this should not be considered an effective
                security measure.

                Refer to RFC 6265, Section 4.1.2.4

            secure (bool): Direct the client to only return the cookie
                in subsequent requests if they are made over HTTPS

                Defaults to False.

                Enabling this can help prevents attackers from reading
                sensitive cookie data.

                Refer RFC 6265, Section 4.1.2.5

            http_only (bool): Direct the client to only transfer the
                cookie with unscripted HTTP requests.

                Default True.

                This is intended to mitigate some forms of cross-site
                scripting.

                Refer to RFC 6265, Section 4.1.2.6

        Raises:
            KeyError: `name` is not a valid cookie name.
            ValueError: `value` is not a valid cookie value.
        """

        if not is_ascii(name):
            raise KeyError('"name" is not ascii encodable')
        if not is_ascii(value):
            raise ValueError('"value" is not ascii encodable')

        name = str(name)
        value = str(value)

        if self._cookies is None:
            self._cookies = SimpleCookie()

        try:
            self._cookies[name] = value
        except CookieError as e:  # pragma: no cover
            # NOTE(tbug): we raise a KeyError here, to avoid leaking
            # the CookieError to the user. SimpleCookie (well, BaseCookie)
            # only throws CookieError on issues with the cookie key
            raise KeyError(str(e))

        if expires:
            # set Expires on cookie. Format is Wdy, DD Mon YYYY HH:MM:SS GMT

            # NOTE(tbug): we never actually need to
            # know that GMT is named GMT when formatting cookies.
            # It is a function call less to just write "GMT" in the fmt string:
            fmt = '%a, %d %b %Y %H:%M:%S GMT'
            if expires.tzinfo is None:
                # naive
                self._cookies[name]['expires'] = expires.strftime(fmt)
            else:
                # aware
                gmt_expires = expires.astimezone(GMT_TIMEZONE)
                self._cookies[name]['expires'] = gmt_expires.strftime(fmt)

        if max_age:
            # RFC 6265 section 5.2.2 says about the max-age value:
            #   "If the remainder of attribute-value contains a non-DIGIT
            #    character, ignore the cookie-av."
            # That is, RFC-compliant response parsers will ignore the max-age
            # attribute if the value contains a dot, as in floating point
            # numbers. Therefore, attempt to convert the value to an integer.
            self._cookies[name]['max-age'] = int(max_age)
        if domain:
            self._cookies[name]['domain'] = domain

        if path:
            self._cookies[name]['path'] = path

        if secure is None:
            is_secure = self.options.secure_cookies_by_default
        else:
            is_secure = secure

        if is_secure:
            self._cookies[name]['secure'] = True

        if http_only:
            self._cookies[name]['httponly'] = http_only

    def unset_cookie(self, name):
        """Unset a cookie in the response

        Clears the contents of the cookie, and instructs the user
        agent to immediately expire its own copy of the cookie.

        In order to successfully remove a cookie, both the
        path and the domain must match the values that were
        used when the cookie was created.

        Args:
            name (str): Cookie Name
        """
        if self._cookies is None:
            self._cookies = SimpleCookie()

        self._cookies[name] = ''
        self._cookies[name]['expires'] = -1

    def __iter__(self):
        # Localized for a little more speed.
        status = self.status
        headers = self._headers
        content_type = self.content_type
        content_length = self.content_length

        # Set Content-Length Header.
        if content_length is not None:
            headers['Content-Length'] = str(content_length)

            # Set Content-Type Header.
            if content_type is not None:
                headers['Content-Type'] = content_type

        elif content_type is None and status not in self._BODILESS_STATUS_CODES:
            headers['Content-Type'] = self._DEFAULT_CONTENT_TYPE

        headers = list(self._headers.items())

        # Load cookies.
        if self._cookies is not None:
            headers += [('Set-Cookie', c.OutputString())
                        for c in self._cookies.values()]

        self._start_response("%s %s" % (status,
                            const.HTTP_STATUS_CODES[status]),
                            headers)

        return super().__iter__()
