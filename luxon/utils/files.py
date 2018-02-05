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
import stat
from io import BytesIO

from luxon.core.cls.singleton import NamedSingleton

class CachedInput(object):
    '''Copies input into a buffer and performs operations on it

    Args:
        io(bytes): bytes object 

    '''

    def __init__(self, io):
        if io is not None:
            self._io = io
        else:
            self._io = BytesIO()

        self._io_pos = 0
        self._cached = BytesIO()
        self._cached_pos = 0

    def read(self, *args, **kwargs):
        '''Copies content of io into a cache and then returns it (from the cache)

        If this fucntion is called when the cache is empty, the contents of of io will
        be copied into it and it (the cache) will be returned.

        If the point in the cache has been shifted back from the end(via seek) 
        and this function is called, it will return the contents of the cache
        from the point to the end. 
        Shifting the point is only possible after io has been cached
        '''
        if self._cached_pos >= self._io_pos:
            io_read = self._io.read(*args, **kwargs)
            bytes_written = self._cached.write(io_read)
            self._io_pos += bytes_written
            self._cached_pos += bytes_written
            self._cached.seek(self._cached_pos-bytes_written)

            return self._cached.read(*args, **kwargs)
        else:
            io_read = self._cached.read(*args, **kwargs)
            self._cached_pos = len(io_read)
            return io_read

    def readline(self, *args, **kwargs):
        '''Copies a line of content from io into a cache and returns it (from the cache)

        Works the same as read()

        '''
        if self._cached_pos >= self._io_pos:
            io_read = self._io.readline(*args, **kwargs)
            bytes_written = self._cached.write(io_read)
            self._io_pos += bytes_written
            self._cached_pos += bytes_written
            self._cached.seek(self._cached_pos-bytes_written)

            return self._cached.readline(*args, **kwargs)
        else:
            io_read = self._cached.readline(*args, **kwargs)
            self._cached_pos = len(io_read)
            return io_read

    def seek(self, pos):
        '''Changes the point position in the cache 

        Args:
            pos(int): new position of point

        '''
        self._cached_pos = pos
        self._cached.seek(pos)

    def nbytes(self):
        '''Returns a readable and writable view over the contents of the cache
        '''
        return self._cached.getbuffer().nbytes


class TrackFile(metaclass=NamedSingleton):
    '''Tracks a given file

    Args:
        file(file): file to be tracked

    '''
    def __init__(self, file):
        self._file = file
        if os.path.isfile(self._file):
            self._modified = os.stat(self._file).st_mtime
        else:
            self._modified = None

    def __call__(self):
        return self.is_modified()

    def is_modified(self):
        '''Checks if file was modified since tracking started

        returns:
            True if modified
        '''
        # If there was never file... check for new file...
        if self._modified is None:
            # If there is now a file...
            if os.path.isfile(self._file):
                self._modified = os.stat(self._file).st_mtime
                return True

        # If there is a file from start...
        if os.path.isfile(self._file):
            # get the modified time of file...
            mtime = os.stat(self._file).st_mtime
            # if modified.
            if mtime != self._modified:
                # update with modified time..
                self._modified = mtime
                return True
            else:
                # if not modified...
                return False
        else:
            # if file is gone it not new..
            return False

    def is_deleted(self):
        '''Checks if file was deleted since tracking started

        Returns:
            True if deleted

        '''
        # If there was a file...
        if self._modified is not None:
            # if file still exisits...
            if os.path.isfile(self._file):
                return False
            # if file doesnt exist anymore...
            return True
        # if it never existed...
        return False

    def clear(self):
        self._modified = None

def is_socket(socket):
    """Is Unix socket

    Args:
        socket (str): Socket path.

    Retrurns:
        Bool whether file is unix socket
    """
    try:
        mode = os.stat(socket).st_mode
        return stat.S_ISSOCK(mode)
    except Exception:
        return False

class FileObject(object):
    __slots__ = ( 'filename', 'type', 'file' )

    def __init__(self, filename, type, file):
        self.filename = filename
        self.type = type
        self.file = file
