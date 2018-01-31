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
from luxon import exceptions
from luxon import GetLogger
from luxon import db
from luxon import js
from luxon.utils.imports import get_class
from luxon.utils.classproperty import classproperty
from luxon.structs.models.fields import BaseField, Integer, parse_defaults

log = GetLogger(__name__)

class BaseModel(object):
    """BaseModel.

    Keyword Args:
        id (str|int): ID to match otherwise all rows are selected.
        query (str): Raw SQL query for Luxon DB API.
        values (dict): Raw parameters for SQL Query.
    """
    __slots__ = ( '_key_id', '_key_field',
                  '_db_api', '_lock', '_id', '_query',
                  '_values',)

    primary_key = None
    _sql = False
    db_charset = 'UTF8'
    db_engine = 'innodb'
    db_default_rows = []
    _declared_fields = None

    def __init__(self, id=None, query=None, values=None, lock=False,
                 declared_fields=None):
        self._id = id
        self._query = query
        self._values = values
        self._lock = lock

        if declared_fields is not None:
            self.__class__._declared_fields = declared_fields

        table = self.table
        result = None

        if self._sql:
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
                                    if row[field] is not None:
                                        self[field] = row[field]
                                self._created = False
                                self._updated = False
                                self._current = model._new.copy()
                                self._new.clear()
                        else:
                            for row in result:
                                model = self.new()
                                for field in row.keys():
                                    if row[field] is not None:
                                        model[field] = row[field]
                                model._current = model._new.copy()
                                model._new.clear()
                                model._created = False
                                model._updated = False

    def __setattr__(self, attr, value):
        if attr[0] == "_":
            super().__setattr__(attr, value)
        else:
            raise KeyError("Model %s:" % self.table +
                           " No such attribute '%s'" % attr) from None

    def __iter__(self):
        return iter(self.transaction)

    def __str__(self):
        return str(self.transaction)

    def __repr__(self):
        return repr(self.transaction)

    def __len__(self):
        return len(self.transaction)

    @classproperty
    def table(cls):
        return cls.__name__.split('.')[-1]

    @classmethod
    def create_table(cls):
        cls._validate_sql_model()

        if cls.primary_key is None:
            raise KeyError("Model %s:" % cls.table +
                           " No primary key") from None

        api = g.config.get('database', 'type')
        driver_cls = api.title()
        driver = get_class('luxon.structs.models.%s:%s' % (api,
                                                           driver_cls,))(cls)
        driver.create()

    @classmethod
    def _validate_sql_model(self):
        if self._sql is False:
            raise TypeError("Model '%s' Not decorated with 'luxon.database_model'"
                           % self.table)

    @classproperty
    def fields(cls):
        if cls._declared_fields is None:
            ignore = ('primary_key', 'fields')
            current_fields = []

            for name in dir(cls):
                if name not in ignore:
                    # NOTE(cfrademan): Hack, dir() shows '__slots__', so it breaks if
                    # attribue is not there while doing getattr. once again, its faster
                    # to ask for forgiveness than permission.
                    try:
                        prop = getattr(cls, name)
                    except AttributeError:
                        prop = None

                    if isinstance(prop, BaseField):
                        current_fields.append((name, prop))
                        prop._table = cls.table
                        prop._name = name

            current_fields.sort(key=lambda x: x[1]._creation_counter)

            cls._declared_fields = OrderedDict(current_fields)

        return cls._declared_fields

class Models(BaseModel):
    __slots__ = ( '_current', '_new', '_deleted', '_args', '_kwargs' )

    def __init__(self, *args, **kwargs):
        self._current = []
        self._new = []
        self._deleted = []
        self._args = args
        self._kwargs = kwargs
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return self.transaction[key]
        except KeyError:
            raise KeyError("Model %s:" % self.table +
                           " No such result/row '%s'" % key) from None

    def __delitem__(self, key):
        try:
            self._deleted.append(self.transaction[key])
            if key + 1 <= len(self._current):
                del self._current[key]
            else:
                del self._new[key]
        except KeyError:
            raise KeyError("Model %s:" % self.table +
                           " No such result/row '%s'" % key) from None

    @property
    def transaction(self):
        """Return current state.
        """
        return self._current + self._new

    def to_json(self):
        """Return as serialized JSON.
        """
        return js.dumps(list(self))

    def new(self):
        """Create new row.

        Creates a new row and returns row model.
        """
        NewModel = type(self.table, (Model,), {})
        NewModel._sql = self._sql
        NewModel.primary_key = self.primary_key
        NewModel.db_charset = self.db_charset
        NewModel.db_engine = self.db_engine
        model = NewModel(declared_fields=self.fields)
        self._new.append(model)
        return model

    def append(self, dict_obj):
        """Append to Models.

        Append new row with fields with relevant values from dictionary.

        Args:
            dict_obj (list): List of Rows.
        """
        model = self.new()
        for item in dict_obj:
            model[item] = dict_obj[item]

    def rollback(self):
        """Rollback.

        Rollback to previous state before commit.
        """
        for model in self.transaction:
            model.rollback()
        self._new.clear()
        self._current += self._deleted
        self._deleted.clear()

    def commit(self):
        """Commit transaction.
        """
        if self._sql:
            try:
                conn = db()
                table = self.table
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
                if self._sql:
                    conn.commit()
                    conn.close()

        for model in self.transaction:
            model.commit()

        self._current = self.transaction
        self._new.clear()
        self._deleted.clear()

    def update(self, list_obj):
        """Update Models.

        Append rows from list object containing objects with relevant field
        columns.

        Args:
            list_obj (list): List of Rows.
        """
        for row in list_obj:
            new = self.new()
            for column in row:
                new[column] = row[column]

class Model(BaseModel):
    __slots__ = ( '_model', '_current', '_new', '_deleted', '_created', )

    def __init__(self, *args, **kwargs):
        self._current = {}
        self._new = {}
        self._created = True
        self._updated = False
        super().__init__(*args, **kwargs)

        # NOTE(cfrademan): Set default values for model object.
        for field in self.fields:
            default = self.fields[field].default
            on_update = self.fields[field].on_update
            if default is not None and field not in self._transaction:
                default = parse_defaults(default)
                default = self.fields[field].parse(default)
                if (field not in self._transaction or
                        self._transaction[field] is None):
                    self._current[field] = default

    def __getattr__(self, attr):
        if attr[0] == '_':
            return super().__getattr__(attr)

        try:
            return self.__getitem__(attr)
        except KeyError as e:
            raise AttributeError(e) from None

    def __setitem__(self, key, value):
        if key in self.fields:
            if (self.primary_key is not None and
                        self[key] is not None and
                        key == self.primary_key.name):
                    raise ValueError("Model %s:" % self.table +
                                     " Cannot alter primary key '%s'"
                                     % key) from None
            self._new[key] = self.fields[key].parse(value)

            if self._created is False:
                self._updated = True
        else:
            raise KeyError("Model %s:" % self.table +
                           " No such field '%s'" % key) from None

    def __getitem__(self, key):
        if key in self.fields:
            try:
                return self._transaction[key]
            except KeyError:
                return None
        else:
            raise KeyError("Model %s:" % self.table +
                           " No such field '%s'" % key) from None

    def __setattr__(self, attr, value):
        if attr[0] == '_':
            super().__setattr__(attr, value)
            return None

        try:
            self.__setitem__(attr, value)
        except KeyError as e:
            raise AttributeError(e) from None

    @property
    def _transaction(self):
        return {**self._current, **self._new}

    @property
    def transaction(self):
        """Return current state.
        """
        # NOTE(cfrademan): KEEP both _transaction and transaction properties.
        # This is for future use.
        return {**self._current, **self._new}

    def to_json(self):
        """Return as serialized JSON.
        """
        return js.dumps(self._transaction)

    def to_dict(self):
        """Return as raw dict.
        """
        return self._transaction.copy()

    def rollback(self):
        """Rollback.

        Rollback to previous state before commit.
        """
        self._new.clear()

    def commit(self):
        """Commit transaction.
        """
        if self._updated is False and self._created is False:
            # NOTE(cfrademan): Short-circuit this method if nothing todo...
            return None

        transaction = {}
        for field in self.fields:
            if field not in self._new:
                on_update = self.fields[field].on_update

                if on_update is not None and self._updated:
                    on_update = parse_defaults(on_update)
                    on_update = self.fields[field].parse(on_update)
                    self._new[field] = on_update

            if (field in self.transaction and
                    self.fields[field].null is False):
                self.fields[field].error('required field')

            if (field in self._transaction and
                    self.fields[field].db):
                transaction[field] = self._transaction[field]

        try:
            if self._sql:
                conn = db()
                table = self.table
                if self.primary_key is None:
                    raise KeyError("Model %s:" % table +
                                   " No primary key") from None

                key_id = self.primary_key.name


                if self._created:
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
                    if isinstance(self.primary_key, Integer):
                        self[self.primary_key.name] = conn.last_row_id()
                    conn.commit()

                elif self._updated:
                    update_id = transaction[key_id]
                    sets = []
                    args = []
                    for field in self._new:
                        if self.primary_key.name != field:
                            if self.fields[field].readonly:
                                self._new[field].error('readonly value')
                            if self.fields[field].db:
                                sets.append('%s' % field +
                                           ' = %s')
                                args.append(self._new[field])

                    if len(sets) > 0:
                        sets = ", ".join(sets)
                        conn.execute('UPDATE %s' % table +
                                   ' SET %s' % sets +
                                   ' WHERE %s' % key_id +
                                   ' = %s',
                                   args + [update_id,])

            self._current = self._transaction
            self._new.clear()
            self._created = False
            self._updated = False
        finally:
            if self._sql:
                conn.commit()
                conn.close()

    def update(self, dict_obj):
        """Update Model.

        Append fields with relevant values from dictionary.

        Args:
            list_obj (list): List of Rows.
        """
        for column in dict_obj:
            new[column] = row[column]
