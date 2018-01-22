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
        #self._name = None
        for kwarg in self._kwargs:
            setattr(self, kwarg, self._kwargs[kwarg])

    @property
    def name(self):
        return self._name

class Integer(BaseField):
    def __init__(self, **kwargs):
        self.auto_increment = None
        super().__init__(**kwargs)

    def parse(self, value):
        return value

class String(BaseField):
    def parse(self, value):
        return value

    @property
    def sql(self):
        try:
            size = self.size
        except AttributeError:
            size = 255

        field = " `%s`" % self.name
        field += " varchar(%s)" % size
        return field

class Boolean(BaseField):
    def parse(self, value):
        return value

    @property
    def sql(self):
        field = " `%s`" % self.name
        field += " tinyint(1)"
        return field

class Datetime(BaseField):
    def parse(self, value):
        return value

class UniqueIndex(BaseField):
    def __init__(self, *args):
        self._index = args
        super().__init__()

    @property
    def sql(self):
        index = 'UNIQUE KEY'
        index += ' `%s` (' % self._name
        fields = []
        for field in self._index:
            fields.append('`%s`' % field.name)
        index += ",".join(fields)
        index += ')'
        return index

class ForeignKey(BaseField):
    def __init__(self, foreign_keys, reference_fields,
                 on_delete='CASCADE', on_update='CASCADE'):
        self._foreign_keys = to_tuple(foreign_keys)
        self._reference_fields = to_tuple(reference_fields)
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()

        super().__init__()

    @property
    def sql(self):
        foreign_keys = []
        references = []
        reference_table = self._reference_fields[0]._table

        for fk in self._foreign_keys:
            foreign_keys.append('`' + fk.name + '`')
        foreign_keys = ",".join(foreign_keys)

        for ref in self._reference_fields:
            references.append('`' + ref.name + '`')
        references = ",".join(references)

        index = 'CONSTRAINT `%s`' % self.name
        index += ' FOREIGN KEY (%s)' % foreign_keys
        index += ' REFERENCES `%s`' % reference_table
        index += ' (%s)' % references
        index += ' ON DELETE %s' % self._on_delete
        index += ' ON UPDATE %s' % self._on_update
        return index
