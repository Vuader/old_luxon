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
from collections import OrderedDict

from luxon import g
from luxon import GetLogger
from luxon.utils.objects import object_name
from luxon.structs.models.fields import BaseField
from luxon.helpers.db import db
from luxon import exceptions
from luxon.utils.imports import get_class
from luxon import js

log = GetLogger(__name__)

def _declared_fields(cls):
    """Return fields in object.

    global_counter() function used in class to set creation_counter property
    on object for class. The creation_counter() keeps a global state of when
    each field is defined in a model. The purpose is primarily for html forms.

    Returns Ordered Dictionary as per when fields are defined.

    The key is the name of the field with value as the field object.
    """
    current_fields = []

    for name in dir(cls):
        # NOTE(cfrademan): Hack, dir() shows '__slots__', so it breaks if
        # attribue is not there while doing getattr. once again, its faster
        # to ask for forgiveness than permission.
        try:
            prop = getattr(cls, name)
        except AttributeError:
            prop = None

        if name != 'primary_key':
            if isinstance(prop, BaseField):
                current_fields.append((name, prop))
                prop._name = name

    current_fields.sort(key=lambda x: x[1]._creation_counter)

    return OrderedDict(current_fields)

class BaseModel(object):
    __slots__ = ( '_key_id', '_key_field', '_declared_fields',
                  '_db_api', '_limit', '_lock')

    primary_key = None
    _sql = False
    db_charset = 'UTF8'
    db_engine = 'innodb'

    def __init__(self, id=None, query=None, values=None, lock=False):
        self._id = id
        self._query = query
        self._values = values
        self._lock = lock
        self._declared_fields = _declared_fields(self)
        table = self.__class__.__name__
        result = None

        if self._sql is True:
            with db() as conn:
                if conn.has_table(table):
                    if self._query is not None:
                        result = conn.execute(self._query, self._values)
                    elif self._id is not None:
                        if self.primary_key is None:
                            raise KeyError("Model %s:" % table +
                                           " No primary key") from None
                        result = conn.execute("SELECT * FROM %s" % table +
                                            " WHERE %s" % self.primary_key.name +
                                            " = %s",
                                            self._id)
                    elif not isinstance(self, Model):
                        result = conn.execute("SELECT * FROM %s" % table)


                    if result is not None:
                        if isinstance(self, Model):
                            result = result.fetchall()
                            if len(result) > 1:
                                muerr = "Multiple rows for model"
                                muerr += " '%s' returned" % table
                                raise exceptions.MultipleOblectsReturned(muerr)
                            if len(result) == 0 and (self._id is not None or
                                                     self._query is not None):
                                nferr = "Query for for model"
                                nferr += " '%s' not found." % table
                                raise exceptions.NotFound(nferr)
                            if len(result) == 1:
                                row = result[0]
                                for field in row.keys():
                                    self[field] = row[field]
                                self._created = False
                        else:
                            for row in result:
                                model = self.new()
                                model._created = False
                                for field in row.keys():
                                    model[field] = row[field]

    def __setattr__(self, attr, value):
        if attr[0] == "_":
            super().__setattr__(attr, value)
        else:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No such attribute '%s'" % attr) from None

    def __iter__(self):
        return iter(self.transaction)

    def __str__(self):
        return str(self.transaction)

    def __repr__(self):
        return repr(self.transaction)

    def sync_db(self):
        if self._sql is False:
            raise TypeError("Model '%s' Not decorated with 'luxon.database_model'"
                           % self.__class__.__name__)

        if self.primary_key is None:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No primary key") from None

        api = g.config.get('database', 'type')
        cls = api.title()
        driver = get_class('luxon.structs.models.%s:%s' % (api, cls,))(self)
        driver.bdcr()

    def __len__(self):
        return len(self.transaction)



class Models(BaseModel):
    __slots__ = ( '_current', '_new', '_deleted', '_args', '_kwargs' )

    def __init__(self, *args, **kwargs):
        self._current = []
        self._new = []
        self._deleted = []
        self._args = args
        self._kwargs = kwargs
        super().__init__(*args, **kwargs)

    def to_json(self):
        return js.dumps(list(self))

    @property
    def transaction(self):
        return self._current + self._new

    def __getitem__(self, key):
        try:
            return self.transaction[key]
        except KeyError:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No such result/row '%s'" % key) from None

    def __delitem__(self, key):
        try:
            self._deleted.append(self.transaction[key])
            if key + 1 <= len(self._current):
                del self._current[key]
            else:
                del self._new[key]
        except KeyError:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No such result/row '%s'" % key) from None

    def new(self):
        NewModel = type(self.__class__.__name__, (Model,), {})
        NewModel._sql = self._sql
        NewModel.primary_key = self.primary_key
        NewModel.db_charset = self.db_charset
        NewModel.db_engine = self.db_engine
        model = NewModel()
        model._declared_fields = self._declared_fields
        self._new.append(model)
        return model

    def append(self, dictionary):
        model = self.new()
        for item in dictionary:
            model[item] = dictionary[item]

    def rollback(self):
        for model in self.transaction:
            model.rollback()
        self._new.clear()
        self._current += self._deleted
        self._deleted.clear()

    def commit(self):
        if self._sql is True:
            try:
                conn = db()
                table = self.__class__.__name__
                if self.primary_key is None:
                    raise KeyError("Model %s:" % table +
                                   " No primary key") from None

                key_id = self.primary_key.name

                for row in self._deleted:
                    delete_id = row[key_id]
                    conn.execute('DELETE FROM %s' % table +
                               ' WHERE %s' % key_id +
                               ' = %s',
                               delete_id)
            finally:
                if self._sql is True:
                    conn.commit()
                    conn.close()
        for model in self.transaction:
            model.commit()
        self._current = self.transaction
        self._new.clear()
        self._deleted.clear()

class Model(BaseModel):
    __slots__ = ( '_model', '_current', '_new', '_deleted', '_created', )

    def __init__(self, *args, **kwargs):
        self._current = OrderedDict()
        self._new = OrderedDict()
        self._created = True
        super().__init__(*args, **kwargs)

    def to_json(self):
        return js.dumps(self.transaction)

    def to_dict(self):
        return self.transaction.copy()

    @property
    def transaction(self):
        return {**self._current, **self._new}

    def __setattr__(self, attr, value):
        if attr[0] == '_':
            super().__setattr__(attr, value)
            return None

        try:
            self.__setitem__(attr, value)
        except KeyError as e:
            raise AttributeError(e) from None

    def __getattr__(self, attr):
        if attr[0] == '_':
            return super().__getattr__(attr)

        try:
            return self.__getitem__(attr)
        except KeyError as e:
            raise AttributeError(e) from None

    def __setitem__(self, key, value):
        try:
            try:
                if (self.transaction[key] is not None and
                        key == self.primary_key.name):
                    raise ValueError("Model %s:" % self.__class__.__name__ +
                                     " Cannot alter primary key '%s'"
                                     % key) from None
            except KeyError:
                pass
            self._new[key] = self._declared_fields[key].parse(value)
        except KeyError:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No such field '%s'" % key) from None

    def __getitem__(self, key):
        if key in self._declared_fields:
            try:
                return self.transaction[key]
            except KeyError:
                return None
        else:
            raise KeyError("Model %s:" % self.__class__.__name__ +
                           " No such field '%s'" % key) from None

    def rollback(self):
        self._new.clear()

    def commit(self):
        try:
            if self._sql is True:
                conn = db()
                table = self.__class__.__name__
                if self.primary_key is None:
                    raise KeyError("Model %s:" % table +
                                   " No primary key") from None

                key_id = self.primary_key.name

                transaction = {}
                for field in self._declared_fields:
                    if field in self.transaction:
                        if self._declared_fields[field].db is True:
                            transaction[field] = self.transaction[field]
                    elif self._declared_fields[field].null is False:
                        self._declared_fields[field].error('required field')

                if self._created is True:
                    query = "INSERT INTO %s (" % table
                    query += ','.join(transaction.keys())
                    query += ')'
                    query += ' VALUES'
                    query += ' ('
                    placeholders = []
                    for ph in range(len(transaction)):
                        placeholders.append('%s')
                    query += ','.join(placeholders)
                    query += ')'
                    conn.execute(query, list(transaction.values()))
                    try:
                        if self.primary_key.auto_increment is True:
                            self[self.primary_key.name] = db.last_row_id()
                    except AttributeError:
                        pass
                    conn.commit()

                else:
                    update_id = transaction[key_id]
                    sets = []
                    args = []
                    for field in self._new:
                        if self._declared_fields[field].readonly is True:
                            self._new[field].error('readonly value')
                        if self._declared_fields[field].db is True:
                            sets.append('%s' % field +
                                       ' = %s')
                            args.append(self._new[field])

                    if len(sets) > 0:
                        sets = ", ".join(sets)
                        conn.execute('UPDATE %s' % table +
                                   ' SET %s' % sets +
                                   ' WHERE %s' % key_id +
                                   ' = %s',
                                   args + [self.primary_key.name,
                                    update_id,])

            self._current = self.transaction
            self._new.clear()
            if self._sql is True:
                conn.commit()
        finally:
            if self._sql is True:
                conn.close()
