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
import os
import hashlib
from pkg_resources import (resource_stream, resource_listdir,
                           resource_isdir, resource_exists)

from luxon.utils.imports import import_module


def create_dir(path, new):
    """Creates a new directory in a given location

    Args:
        path (str): location of new directory
        new (str): name of new directory
    """
    new = os.path.normpath('%s%s' % (path, new))
    if not os.path.exists(new):
        os.makedirs(new)
        print('Created directory: %s' % new)


def copy_file(module, path, src, dst, update=True):
    """Copy Resource

    Given a module and a resource name this function will copy that resource into a given destination file.
    If a file with that name already exists and update = False, a new file with .default appended to the name
    will be created and used as the destination.
    If update = True, the file it will be overwritten

    Args:
         module: package from which a resource will be copied
         path (str): path of destination directory
         src (str): name of resource to be copied
         dst (str): destination file to be copied to
         update (bool): whether existing file should be updated
    """
    try:
        import_module(module)
    except ImportError as e:
        print("Import Error %s\n%s" % (module, e))
        exit()

    dst = os.path.normpath("%s/%s" % (path, dst))
    if resource_exists(module, src):
        src_file = resource_stream(module, src).read()
        if not os.path.exists(dst):
            with open(dst, 'wb') as handle:
                handle.write(src_file)
                print("Created %s" % dst)
        else:
            if update is False:
                dst = "%s.default" % (dst,)
                if not os.path.exists(dst):
                    with open(dst, 'wb') as handle:
                        handle.write(src_file)
                        print("Created %s" % dst)
            else:
                src_sig = hashlib.md5(src_file)
                dst_file = open(dst, 'rb').read()
                dst_sig = hashlib.md5(dst_file)
                if src_sig.hexdigest() != dst_sig.hexdigest():
                    with open(dst, 'wb') as handle:
                        handle.write(src_file)
                        print("Updated %s" % dst)


def recursive_copy(local, module, path):
    """Copies a resource in the form of a directory

    Recursively copies all the files in the resource directory.
    A series of new files will be created in the given directory
    to mirror the files in the resource

    Args:
        local (str): directory into which resource will be copied
        module: package to be copied from
        path (str): resource name

    """
    if resource_isdir(module, path):
        for filename in resource_listdir(module, path):
            fullname = path + '/' + filename
            if resource_isdir(module, fullname):
                create_dir(local, '/%s' % filename)
                recursive_copy("%s/%s" % (local, filename), module, fullname)
            else:
                copy_file(module, local, fullname, filename)
