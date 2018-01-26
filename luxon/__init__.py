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
import builtins

from luxon import metadata

# The big 'g' for accessing process wide globals.
from luxon.core.globals import luxon_globals as g
from luxon.utils.middleware import middleware
from luxon.core.register import resource as register_resource
from luxon.core.register import resources as register_resources
from luxon.core.register import middleware as register_middleware
from luxon.core.register import model as database_model

# We must start the logger before anything else.
# This is to ensure no other modules try configure the logger before us.
# Also if another log attempts to log without using our logger it will
# implement basicconfiguration for handlers etc. Hence we ensure we the first
# to configure it.
from luxon.core.logger import GetLogger
log = GetLogger()

# Below is for conveniance.
from luxon.core import cls
from luxon.utils import js
from luxon.helpers.jinja2 import render_template
from luxon.helpers.redis import strict as redis
from luxon.helpers.db import db
from luxon.structs.models.model import Models
from luxon.structs.models.model import Model
from luxon.structs.models import fields
from luxon.core.config import Config

__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright
__identity__ = metadata.identity
