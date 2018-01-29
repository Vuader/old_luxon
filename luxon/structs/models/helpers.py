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

from luxon.structs.models.fields import BaseField

def declared_fields(cls):
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
