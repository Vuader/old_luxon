#!/usr/bin/env python
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
import sys
import argparse

from luxon import metadata
from luxon.core.servers.web import server as web_server

def server(args):
    web_server(app_root=args.path, ip=args.ip, port=args.port)

def main(argv):
    description = metadata.description + ' ' + metadata.version
    print("%s\n" % description)

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('path',
                        help='Application root path')

    group.add_argument('-s',
                       dest='funcs',
                       action='append_const',
                       const=server,
                       help='Start Internal Testing Server (requires gunicorn)')
    parser.add_argument('--ip',
                       help='Binding IP Address (127.0.0.1)',
                       default='127.0.0.1')
    parser.add_argument('--port',
                        help='Binding Port (8080)',
                        default='8080')

    args = parser.parse_args()

    if args.funcs is not None:
        for func in args.funcs:
            func(args)

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
