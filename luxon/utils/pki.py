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

import OpenSSL
from OpenSSL import crypto
import base64


def sign(key_file, data, passphrase=None, digest='sha512'):
    """Signature Generator


    Creates signature form a public key and signes a piece of data with it


    Args:
        key_file (file): Private key to sign with

        data (file): data to be signed
        passphrase (str): optional passhrase
        digest (str): message digest, sha512 by default

    returns:
        b64encoded signature
    """

    with open(key_file, "r") as key_file:
        key = key_file.read()

    if key.startswith('-----BEGIN '):
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM,
                                      key,
                                      passphrase=passphrase)
    else:
        pkey = crypto.load_pkcs12(key, passphrase=passphrase).get_privatekey()

    signature = OpenSSL.crypto.sign(pkey, data, digest)
    return base64.b64encode(signature)


def verify(cert_file, signature, data, digest='sha512'):

    """Verify Signature

    Use public key to verify signature on signed data

    Args:
        cert_file (file): Signing Certificate
        signature (str): Signature returned by sign function
        data (file): data to be verified
        digest (str): message digest, sha512 by default

    Return:
        True if verified
    """
    signature = base64.b64decode(signature)
    with open(cert_file, "r") as cert_file:
        cert = cert_file.read()

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

    try:
        OpenSSL.crypto.verify(cert, signature, data, digest)
    except OpenSSL.crypto.Error as e:
        raise ValueError("PKI Unable to verify signature '%s'" % e) from None
        return False

    return True
