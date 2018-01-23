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
from luxon.utils.global_counter import global_counter
from luxon.utils.cast import to_tuple

class BaseField(object):
    _table = None

    def __init__(self, **kwargs):
        self._creation_counter = global_counter()
        self._value = None
        self._kwargs = kwargs
        for kwarg in self._kwargs:
            setattr(self, kwarg, self._kwargs[kwarg])

    @property
    def name(self):
        return self._name

class String(BaseField):
    def parse(self, value):
        return value

class TinyInt(BaseField):
    def parse(self, value):
        return value

class SmallInt(BaseField):
    def parse(self, value):
        return value

class MediumInt(BaseField):
    def parse(self, value):
        return value

class Integer(BaseField):
    def parse(self, value):
        return value

class BigInt(BaseField):
    def parse(self, value):
        return value

class DateTime(BaseField):
    def parse(self, value):
        return value

class TinyBlob(BaseField):
    def parse(self, value):
        return value

class Blob(BaseField):
    def parse(self, value):
        return value

class MediumBlob(BaseField):
    def parse(self, value):
        return value

class LongBlob(BaseField):
    def parse(self, value):
        return value

class TinyText(BaseField):
    def parse(self, value):
        return value

class Text(BaseField):
    def parse(self, value):
        return value

class MediumText(BaseField):
    def parse(self, value):
        return value

class LongText(BaseField):
    def parse(self, value):
        return value

class Enum(BaseField):
    def parse(self, value):
        return value

class Boolean(SmallInt):
    def parse(self, value):
        return value

class UniqueIndex(BaseField):
    def __init__(self, *args):
        self._index = args
        super().__init__()

class ForeignKey(BaseField):
    def __init__(self, foreign_keys, reference_fields,
                 on_delete='CASCADE', on_update='CASCADE'):
        self._foreign_keys = to_tuple(foreign_keys)
        self._reference_fields = to_tuple(reference_fields)
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()
        super().__init__()

