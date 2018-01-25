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
from datetime import datetime as py_datetime
from decimal import Decimal as PyDecimal

from luxon.utils.global_counter import global_counter
from luxon.utils.cast import to_tuple
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.exceptions import FieldError
from luxon.utils.timezone import to_utc
from luxon.utils.timezone import TimezoneUTC

def parse_defaults(value):
    if hasattr(value, '__call__'):
        value = value()

    if isinstance(value, str):
        value = "'" + value + "'"
    elif isinstance(value, bool):
        if value is True or value == 1:
            value = 1
        else:
            value = 0

    return value

class BaseField(object):

    """Field Class.

    Provides abstractions for most common database data types.

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        columns (int): Number of columns to display for text field.
        hidden (bool): To hide field from forms.
        enum (list): List of possible values. Only for ENUM.

    Properties:
        name (str): Name of field.
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        columns (int): Number of columns to display for text field.
        hidden (bool): To hide field from forms.
        enum (list): List of possible values. Only for ENUM.

    """
    __slots__ = ('length', 'min_length', 'max_length', 'null', 'default',
                 'db', 'label', 'placeholder', 'readonly', 'prefix',
                 'suffix', 'columns' ,'hidden', 'enum', '_name', '_table',
                 '_value', '_creation_counter', 'm', 'd', 'on_update')

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None):
        self._creation_counter = global_counter()
        self._value = None

        self.length = length
        self.min_length = min_length
        if max_length is None:
            self.max_length = length
        else:
            self.max_length = max_length
        self.null = null
        self.default = default
        self.on_update = on_update
        self.db = db
        self.label = label
        self.placeholder = placeholder
        self.readonly = readonly
        self.prefix = prefix
        self.suffix = suffix
        self.columns = columns
        self.hidden = hidden
        self.enum = enum

    @property
    def name(self):
        return self._name

    def error(self, msg, value=None):
        raise FieldError(self.name, self.label, msg, value)

    def parse(self, value):
        if hasattr(value, '__len__'):
            if self.min_length is not None and len(value) < self.min_length:
                self.error("Minimum length '%s'" % self.min_length, value)
            if self.max_length is not None and len(value) > self.max_length:
                self.error("Exceeding max length '%s'" % self.max_length, value)
        if isinstance(value, (int, float, PyDecimal,)):
            if self.min_length is not None and value < self.min_length:
                self.error("Minimum value '%s'" % self.min_length, value)
            if self.max_length is not None and value > self.max_length:
                self.error("Exceeding max value '%s'" % self.max_length, value)


        if self.null is False and (value is None or value.strip() == ''):
            self.error('Empty field value (required)', value)
        return value

class String(BaseField):
    def parse(self, value):
        value = if_bytes_to_unicode(value)
        if not isinstance(value, str):
            self.error('Text value required)', value)
        value = super().parse(value)
        return value

class Integer(BaseField):
    def parse(self, value):
        try:
            value = int(value)
        except ValueError:
            self.error('Integer value required)', value)
        value = super().parse(value)
        return value

class Float(BaseField):
    """Float Field.

    The FLOAT and DOUBLE types represent approximate numeric data values. MySQL
    uses four bytes for single-precision values and eight bytes for
    double-precision values.
    """
    def __init__(self, m, d):
        self.m = m
        self.d = d
        super().__init__()

    def parse(self, value):
        try:
            value = float(value)
        except ValueError:
            self.error('Float value required', value)
        value = super().parse(value)
        return value

class Double(Float):
    """Double Field.

    The FLOAT and DOUBLE types represent approximate numeric data values. MySQL
    uses four bytes for single-precision values and eight bytes for
    double-precision values.
    """
    def parse(self, value):
        try:
            value = float(value)
        except ValueError:
            self.error('Float/Double value required', value)
        value = super().parse(value)
        return value

class Decimal(BaseField):
    def __init__(self, m, d):
        super().__init__()

    def parse(self, value):
        try:
            value = PyDecimal(value)
        except ValueError:
            self.error('Decimal value required', value)
        value = super().parse(value)
        return value


class TinyInt(Integer):
    pass

class SmallInt(Integer):
    pass

class MediumInt(Integer):
    pass

class BigInt(Integer):
    pass

class DateTime(BaseField):
    def parse(self, value):
        try:
            if isinstance(value, py_datetime):
                if value.tzinfo is not None:
                    value = to_utc(value)
                else:
                    value = to_utc(value, src=TimezoneUTC())
            else:
                value = to_utc(value, src=TimezoneUTC())

        except ValueError as e:
            self.error('DateTime value required (%s)' % e, value)
        return value

class Blob(BaseField):
    def parse(self, value):
        value = super().parse(value)
        return value

class TinyBlob(Blob):
    pass

class MediumBlob(Blob):
    pass

class LongBlob(Blob):
    pass

class Text(String):
    pass

class TinyText(String):
    pass

class MediumText(String):
    pass

class LongText(String):
    pass

class Enum(String):
    def parse(self, value):
        if value not in self.enum:
            self.error('Invalid option', value)
        value = super().parse(value)
        return value

class Boolean(SmallInt):
    def parse(self, value):
        if value is None:
            value = False
        elif isinstance(value, int):
            if value == 0:
                value = False
            else:
                value = True
        if not isinstance(value, bool):
            self.error('Invalid True/False Boolean value', value)
        return value

class UniqueIndex(BaseField):
    def __init__(self, *args):
        self._index = args
        super().__init__()

class ForeignKey(BaseField):
    def __init__(self, foreign_keys, reference_fields,
                 on_delete='CASCADE', on_update='CASCADE'):
        on = [ 'NO ACTION', 'RESTRICT', 'SET NULL', 'SET DEFAULT' , 'CASCADE' ]
        on_delete = on_delete.upper()
        on_update = on_update.upper()

        if on_delete not in on:
            raise("Invalid on delete option table '%s'" % self._table)

        if on_update not in on:
            raise("Invalid on delete option table '%s'" % self._table)

        self._foreign_keys = to_tuple(foreign_keys)
        self._reference_fields = to_tuple(reference_fields)
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()
        super().__init__()
