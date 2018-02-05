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

class Constants(object):
    '''Simulates Constant variables in python

    Create new variable attribute in a constants object that can't be rewritten.
    Used in the constants module to list all the constants (HTTP status codes etc.)
    that are needed 

    Example:
        .. code:: python


            _const = Constants()

            _const.TEXT_HTML = 'text/html; charset=utf-8'
            _const.TEXT_PLAIN = 'text/plain; charset=utf-8'
            _const.TEXT_CSS = 'text/css; charset=utf-8'
            _const.IMAGE_JPEG = 'image/jpeg'
            _const.IMAGE_GIF = 'image/gif'
            _const.IMAGE_PNG = 'image/png'
            _const.APPLICATION_XML = 'application/xml; charset=utf-8'
            _const.APPLICATION_JSON = 'application/json; charset=utf-8'
            _const.APPLICATION_OCTET_STREAM = 'application/octet-stream'
            _const.APPLICATION_FORM_DATA = 'application/x-www-form-urlencoded'
            _const.APPLICATION_PDF = 'application/pdf'
    '''

    class ConstError(TypeError):
        pass

    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)

    def __getitem__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        if attr in self.__dict__:
            raise self.ConstError("Can't rebind constant(%s)" % attr)

        if isinstance(value, ( str, tuple, int, float )):
            self.__dict__[attr] = value
        elif isinstance(value, list):
            self.__dict__[attr] = tuple(value)
        elif isinstance(value, dict):
            self.__dict__[attr] = Constants()
            self.__dict__[attr].__dict__.update(value)
        else:
            raise self.ConstError("Can't bind constant(%s) value" % attr,
                                  " must be of type"
                                  " str|list|tuple|dict|float|int")

    def __repr__(self):
        return 'Constants' + str(tuple(self.__dict__.items()))

    def __str__(self):
        return 'Constants' + str(tuple(self.__dict__.items()))
