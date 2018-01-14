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
import string
import cgi

from luxon.utils.strings import unquote_string

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
