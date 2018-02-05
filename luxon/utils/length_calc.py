# -*- coding: utf-8 -*-
# Copyright (c) 2018 Hieronymus Crouse, Christiaan Rademan.
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

def length_calc(min_length, max_length, signed, octets, type=int):
    """Minimum Maximum Lenght Calculator.

    Checks if given minimum length and maximum lenght of field are valid
    according to whether or not it is signed and how big the field is in octets

    Args:
        min_length (int): min length given by user.
        max_length (int): max length given by user.
        signed (bool): whether or not field is signed
        octets (int): size of field in octets
        type (type): String or Integer type.

    Returns:
        Valid minimum length and maximum length as a tuple
    """
    bits = octets * 8
    default = 2**(bits)

    if type == str or type == bytes or type == bytearray:
        signed = False
        default = default // 8
    elif type == int:
        default = default - 1
        signed_default = (default + 1) // 2
    else:
        raise ValueError('Unsupported type provided')

    if signed is True:
        if min_length is None or max_length is None:
            min_length = -signed_default
            max_length = signed_default-1
        else:
            if (min_length<-signed_default or min_length>max_length or
                    min_length>signed_default):
                raise ValueError("Define Valid Minimum Lenght")
            if (max_length<-signed_default or max_length<min_length or
                    max_length>signed_default-1):
                raise ValueError("Define Valid Maximum Lenght")

    else:
        if min_length is None or max_length is None:
            min_length = 0
            max_length = default
        else:
            if min_length <0 or min_length>max_length or min_length>default:
                raise ValueError("Define Valid Minimum Lenght")
            if max_length>default or max_length<min_length or max_length<0:
                raise ValueError("Define Valid Maximum Lenght")

    return (min_length, max_length)
