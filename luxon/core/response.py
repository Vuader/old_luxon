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

from io import BytesIO
from collections import OrderedDict

from luxon import g
from luxon import constants as const
from luxon import exceptions
from luxon.utils.encoding import if_unicode_to_bytes
from luxon.utils import js

class ResponseBase(object):
    """Base Class Represents response to a client's request.

    Args:
        *: All other args are for specific initilization of parent classes.

    Keyword Args:
        *: All other kwargs are for specific initilization of parent classes.

    Attributes:
        status (int): Status code. (e.g. for HTTP '200').
        content_type (str): Content-Type header.
        content_length (int): Size of response body.
    """
    _STREAM_BLOCK_SIZE = 8 * 1024  # 8 KiB
    _DEFAULT_CONTENT_TYPE = const.TEXT_PLAIN
    _DEFAULT_ENCODING = 'UTF-8'
    _DEFAULT_CONTENT_TYPE = const.APPLICATION_JSON

    __slot__ = (
        'content_type',
        '_stream',
        '_total_rows',
        '_filtered_rows',
        '_view_rows',
        '_headers',
    )

    """Base Session / Request Class.
    """
    def __init__(self, *args, **kwargs):
        """Setup Response object.

        Args:
            app (object): Application Object.
            args (tuple): Args provided to application interface.
            kwargs (dict): Kwargs provided to application interface.
        """
        self.content_type = None
        self._stream = None
        self._total_rows = None
        self._filtered_rows = None
        self._view_rows = None
        self._headers = {}

    def __post__(self, app, *args, **kwargs):
        """Post Request Response prepare.

        Args:
            app (object): Application Object.
            args (tuple): Args provided to application interface.
            kwargs (dict): Kwargs provided to application interface.
        """
        pass

    @property
    def rows(self):
        return (self._total_rows, self._filtered_rows)

    @rows.setter
    def rows(self, value):
        if not isinstance(value, (tuple, list,)):
            raise ValueError('Invalid rows value type set on response object')

        try:
            total_rows, view_rows = value
            self._total_rows = int(total_rows)
            self._view_rows = int(view_rows)
            if self._view_rows > self._total_rows:
                raise ValueError('View rows cannot' +
                                 ' exceed total rows') from None
            self._filtered_rows = total_rows - view_rows

            try:
                self.set_header('X-Total-Rows', str(self._total_rows))
                self.set_header('X-View-Rows', str(self._view_rows))
                self.set_header('X-Filtered-Rows', str(self._filtered_rows))
            except AttributeError:
                pass

        except ValueError:
            raise ValueError('Invalid rows value type set on response object')

    @property
    def content_length(self):
        """Value of bytes in response.

        Returns:
            int: total octects for response.
        """
        try:
            return self._stream.getbuffer().nbytes
        except AttributeError:
            pass

        try:
            return self._stream.nbtyes()
        except AttributeError:
            pass

        try:
            return len(self._stream)
        except TypeError:
            return None

    def body(self, obj):
        """Set Response Body.

        Accepts following objects:
            'str', and 'bytes', if str will be encoded to bytes.
            file, iter like objects must return bytes.
            OrderedDict, dict and list will be translated json
            and encoded to 'UTF-8'

        Args:
            obj (object): Any valid object for response body.
        """
        if isinstance(obj, (str, bytes,)):
            # If Body is string, bytes.
            obj = if_unicode_to_bytes(obj)
            if self.content_type is None:
                self.content_type = self._DEFAULT_CONTENT_TYPE
            self._stream = obj
        elif isinstance(obj, (OrderedDict, dict, list, tuple,)):
            # If JSON serializeable object.
            self.content_type = const.APPLICATION_JSON
            self._stream = if_unicode_to_bytes(js.dumps(obj))
        elif hasattr(obj, 'json'):
            # If JSON serializeable object.
            self.content_type = const.APPLICATION_JSON
            self._stream = if_unicode_to_bytes(obj.json)
        elif hasattr(obj, 'read') or hasattr(obj, '__iter__'):
            # If body content behaves like file.
            if self.content_type is None:
                self.content_type = const.APPLICATION_OCTET_STREAM
            self._stream = obj
        else:
            raise ValueError('resource not returning acceptable object %s' %
                            type(obj))

    def write(self, value):
        """Write bytes to response body.

        Args:
            value (bytes): Data to be written.

        Returns:
            int: The number of bytes written.
        """
        value = if_unicode_to_bytes(value)

        if not isinstance(self._stream, BytesIO):
            self._stream = BytesIO()

        length = self._stream.write(value)

        if self.content_type is None:
            self.content_type = self._DEFAULT_CONTENT_TYPE

        return length

    def __iter__(self):
        _STREAM_BLOCK_SIZE = self._STREAM_BLOCK_SIZE

        _stream = self._stream

        try:
            # Rewind file like object to beginning
            _stream.seek(0)
        except Exception:
            pass

        try:
            while True:
                chunk = _stream.read(_STREAM_BLOCK_SIZE)
                if not chunk:
                    break
                yield chunk
        except AttributeError:
            # If iterable body...
            try:
                for i in range(0, len(_stream), _STREAM_BLOCK_SIZE):
                    yield _stream[i:i + _STREAM_BLOCK_SIZE]
            except TypeError:
                pass

            yield b''

    def read(self):
        try:
            self._stream.seek(0)
            return self._stream.read()
        except AttributeError:
            return self._stream

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.status)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.status)
