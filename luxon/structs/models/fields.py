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
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
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
                 '_value', '_creation_counter', 'm', 'd', 'on_update',
                 'password', 'signed')

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):
        self._creation_counter = global_counter()
        self._value = None

        self.length = length
        self.min_length = min_length
        if max_length is None:
            self.max_length = length
        else:
            self.max_length = max_length
        self.signed = signed
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
        self.password = password

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
    """String Field.

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        columns (int): Number of columns to display for text field.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def parse(self, value):
        value = if_bytes_to_unicode(value)
        if not isinstance(value, str):
            self.error('Text value required)', value)
        value = super().parse(value)
        return value

class Integer(BaseField):
    """Integer Field.

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def parse(self, value):
        try:
            value = int(value)
        except ValueError:
            self.error('Integer value required)', value)
        value = super().parse(value)
        return value

class Float(BaseField):
    """Float Field.

    The FLOAT type represent approximate numeric data values. MySQL uses four
    bytes for single-precision values. Keep in mind SQLLite uses REAL numbers
    with double floating points.

    For values which are more artefacts of nature which can't really be measured
    exactly anyway, float/double are more appropriate. For example, scientific data
    would usually be represented in this form. Here, the original values won't be
    "decimally accurate" to start with, so it's not important for the expected
    results to maintain the "decimal accuracy". Floating binary point types are
    much faster to work with than decimals.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
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

    The DOUBLE type represent approximate numeric data values. MySQL
    uses eight bytes for double-precision values. Keep in mind SQLLite uses
    REAL numbers with double floating points.

    For values which are more artefacts of nature which can't really be measured
    exactly anyway, float/double are more appropriate. For example, scientific data
    would usually be represented in this form. Here, the original values won't be
    "decimally accurate" to start with, so it's not important for the expected
    results to maintain the "decimal accuracy". Floating binary point types are
    much faster to work with than decimals.

    Doubles provide more accuracy vs floats. However in Python floats are
    doubles.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
    """
    def parse(self, value):
        try:
            value = float(value)
        except ValueError:
            self.error('Float/Double value required', value)
        value = super().parse(value)
        return value

class Decimal(BaseField):
    """Decimal Field.

    For values which are "naturally exact decimals" it's good to use decimal.
    This is usually suitable for any concepts invented by humans: financial
    values are the most obvious example, but there are others too. Consider the
    score given to divers or ice skaters, for example.

    Keep in mind in SQLite this is REAL numbers with double floating points.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
    """
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
    """Tiny Integer Field.

    1 Octet Integer
    Minimum value -128
    Maximum value 127

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        if signed is True:
            mmin = -128
            mmax = 127
        else:
            mmin = 0
            mmax = 255

        super().__init__(length=None, min_length=mmin, max_length=mmax,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False)

class SmallInt(Integer):
    """Small Integer Field.

    2 Octet Integer
    Minimum value -32768
    Maximum value 32767

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        if signed is True:
            mmin = -32768
            mmax = 32767
        else:
            mmin = 0
            mmax = 65535

        super().__init__(length=None, min_length=mmin, max_length=mmax,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False)

class MediumInt(Integer):
    """Medium Integer Field.

    3 Octet Integer
    Minimum value -8388608
    Maximum value 8388607

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Wether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Wether field can be updated.
        prefix (str): Text placed infront of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        if signed is True:
            mmin = -8388608
            mmax = 8388607
        else:
            mmin = 0
            mmax = 16777215

        super().__init__(length=None, min_length=mmin, max_length=mmax,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False)

class BigInt(Integer):
    """Big Integer Field.
    """
    pass

class DateTime(BaseField):
    """DateTime Field.
    """
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

class PyObject(BaseField):
    """Python Object Field.
    """
    def __init__(self):
        super().__init__()
        self.db = False

    def parse(self, value):
        return value

class Blob(BaseField):
    """Blob Field.
    """
    def parse(self, value):
        value = super().parse(value)
        return value

class TinyBlob(Blob):
    """Tiny Blob Field.
    """
    pass

class MediumBlob(Blob):
    """Medium Blob Field.
    """
    pass

class LongBlob(Blob):
    """Long Blob Field.
    """
    pass

class Text(String):
    """Text Field.
    """
    pass

class TinyText(String):
    """Tiny Text Field.
    """
    pass

class MediumText(String):
    """Medium Text Field.
    """
    pass

class LongText(String):
    """Long Text Field.
    """
    pass

class Enum(String):
    """Enum Field.
    """
    def __init__(self, *args):
        super().__init__()
        self.enum = args

    def parse(self, value):
        if value not in self.enum:
            self.error('Invalid option', value)
        return value

class Uuid(String):
    """UUID Field.
    """
    def __init__(self, *args):
        super().__init__()
        self.length = 36
        self.enum = args

    def parse(self, value):
        value = super().parse(value)
        return value

class Boolean(SmallInt):
    """Boolean Field.
    """
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
    """Unique Index.
    """
    def __init__(self, *args):
        self._index = args
        super().__init__()

class ForeignKey(BaseField):
    """Foreign Key.
    """
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
