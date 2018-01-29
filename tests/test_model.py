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
from decimal import Decimal as PyDecimal

import pytest

from luxon import register_resource
from luxon import database_model

from luxon import Model
from luxon import Models
from luxon.structs.models.fields import String
from luxon.structs.models.fields import Integer
from luxon.structs.models.fields import Float
from luxon.structs.models.fields import Double
from luxon.structs.models.fields import Decimal
from luxon.structs.models.fields import DateTime
from luxon.structs.models.fields import PyObject
from luxon.structs.models.fields import Blob
from luxon.structs.models.fields import Text
from luxon.structs.models.fields import Enum
from luxon.structs.models.fields import Boolean
from luxon.structs.models.fields import UniqueIndex
from luxon.structs.models.fields import ForeignKey

from luxon import g
from luxon import Config
from luxon import db

g.config = config = Config()
g.config['database'] = {}
g.config['database']['type'] = 'sqlite3'
g.config['database']['database'] = 'test.db'


@database_model()
class Model_Test2(Models):
    id = Integer(length=11, null=True)
    primary_key = id
    stringcol = String(length=128)
    floatcol = Float(4,4)
    doublecol = Double(4,4)
    decimalcol = Decimal(4,4)
    datetimecol = DateTime(4,4)
    pyobject = PyObject()
    blob = Blob()
    text = Text()
    enum = Enum('option1', 'option2')
    boolean = Boolean()
    unique_index2 = UniqueIndex(stringcol)

@database_model()
class Model_Test1(Models):
    id = Integer(length=11, null=True)
    primary_key = id
    stringcol = String(length=128)
    floatcol = Float(4,4)
    doublecol = Double(4,4)
    decimalcol = Decimal(4,4)
    datetimecol = DateTime(4,4)
    pyobject = PyObject()
    blob = Blob()
    text = Text()
    enum = Enum('option1', 'option2')
    boolean = Boolean()
    unique_index1 = UniqueIndex(stringcol)
    fk = ForeignKey((stringcol), (Model_Test2.stringcol))


def test_model():
    global test1, test2

    with db() as conn:
        try:
            conn.execute('DROP TABLE %s' % 'Model_Test1')
            conn.execute('DROP TABLE %s' % 'Model_Test2')
        except:
            pass

    test1 = Model_Test1()
    test2 = Model_Test2()
    test2.sync_db()
    test1.sync_db()
    new = test2.new()
    new['stringcol'] = 'String Col'
    new['floatcol'] = 123.22
    new['doublecol'] = 123.22
    new['decimalcol'] = 123.22
    new['datetimecol'] = '1983-01-17 00:00:00'
    new['pyobject'] = {}
    new['blob'] = b'Binary Data'
    new['text'] = "string of text"
    new['enum'] = 'option1'
    new['boolean'] = True
    test2.commit()
    new = test1.new()
    new['stringcol'] = 'String Col'
    new['floatcol'] = 123.22
    new['doublecol'] = 123.22
    new['decimalcol'] = 123.22
    new['datetimecol'] = '1983-01-17 00:00:00'
    new['pyobject'] = {}
    new['blob'] = b'Binary Data'
    new['text'] = "string of text"
    new['enum'] = 'option1'
    new['boolean'] = True
    test1.commit()
    assert isinstance(test1[0]['pyobject'], dict)
    test1 = Model_Test1()
    assert isinstance(test1[0]['id'], int)
    assert isinstance(test1[0]['floatcol'], float)
    assert isinstance(test1[0]['doublecol'], float)
    assert isinstance(test1[0]['decimalcol'], PyDecimal)
    assert isinstance(test1[0]['blob'], bytes)
    assert isinstance(test1[0]['text'], str)
    assert isinstance(test1[0]['enum'], str)
    assert isinstance(test1[0]['boolean'], bool)










