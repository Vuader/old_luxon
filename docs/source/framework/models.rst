.. _models:

Models - ORM
============
A model is the data structure of information. It contains the fields, types and restrictions of the data you’re storing. A model can map to a single database table.

The basics:

    * Each model is a Python class that subclasses luxon.models or luxon.model
    * luxon.model is for a single object with fields.
    * luxon.models contains list/rows of objects with fields.
    * Using models optionally gives you conveniantly maintained and generated database.

Models Class
------------

.. autoclass:: luxon.Models
    :members:

Model Class
-----------

.. autoclass:: luxon.Model
    :members:

Fields
------

**Conveniantly accessible using 'from luxon import fields'**

.. autoclass:: luxon.String
    :members:
    :inherited-members:

.. autoclass:: luxon.Integer
    :members:
    :inherited-members:

.. autoclass:: luxon.Float
    :members:
    :inherited-members:

.. autoclass:: luxon.Double
    :members:
    :inherited-members:

.. autoclass:: luxon.Decimal
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyInt
    :members:
    :inherited-members:

.. autoclass:: luxon.SmallInt
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumInt
    :members:
    :inherited-members:

.. autoclass:: luxon.BigInt
    :members:
    :inherited-members:

.. autoclass:: luxon.DateTime
    :members:
    :inherited-members:

.. autoclass:: luxon.PyObject
    :members:
    :inherited-members:

.. autoclass:: luxon.Blob
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.LongBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.Text
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyText
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumText
    :members:
    :inherited-members:

.. autoclass:: luxon.Enum
    :members:
    :inherited-members:

.. autoclass:: luxon.Boolean
    :members:
    :inherited-members:

.. autoclass:: luxon.Uuid
    :members:
    :inherited-members:

.. autoclass:: luxon.UniqueIndex
    :members:
    :inherited-members:

.. autoclass:: luxon.ForeignKey
    :members:
    :inherited-members:
