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


def object_name(obj):
    """Generates a name for an object from it's module and class


    Args:
        obj (object): any object to be named

    Returns:
        String naming the object

    """
    try:
        try:
            return obj.__module__ + '.' + obj.__name__
        except TypeError:
            return obj.__name__
    except AttributeError:
        try:
            val = obj.__class__.__module__
            val += '.' + obj.__class__.__name__
            return val.replace('builtins.','')
        except TypeError:
            return obj.__class__.__name__
        except AttributeError:
            return obj

    raise ValueError("Cannot determine object name '%s'" % type(obj)) from None

#Not tested yet
def dict_value_property(dictionary, key):
    """Create a read-only property

    Args:
        dictionary (dict): Dictionary in object..
        key (str): Case-sensitive dictionary key.

    Returns:
        A property instance that can be assigned to a class variable.
    """

    def fget(self):
        dictionary_obj = getattr(self, dictionary)
        try:
            return dictionary_obj[key] or None
        except KeyError:
            return str(dictionary_obj)

    return property(fget)
