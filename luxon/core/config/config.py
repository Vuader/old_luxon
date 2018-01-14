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

import configparser
import json

from luxon.utils import js
from luxon.core.config.defaults import defaults
from luxon.structs.container import Container

class Config(configparser.ConfigParser):
    """Tachyonic Python ConfigParser extended.

    You can find complete set of methods from Python ConfigParser documentation.

    Alterations in behaviour:
        * Sections are case-insenstive too.
        * Addition can use attributes to get section, options without spaces.

    However the methods within here only to provide extended functionality.

    Args:
        config_file (str): Optional config file or dict to load.
    """
    __slots__ = ()

    def __init__(self, config_file=None):
        super().__init__(dict_type=Container)
        self.read_dict(defaults)
        if config_file is not None:
            self.load(config_file)

    def load(self, config_file, encoding=None):
        """Load Configuration file.

        Args:
            config_file (str): Path / Location to configuration file.
        """
        if encoding is not None:
            with open(config_file, 'r', encoding=encoding) as f:
                super().read_file(f)
        else:
            with open(config_file, 'r') as f:
                super().read_file(f)

    def __getattr__(self, key):
        class Proxy(object):
            def __init__(self, section):
                self._config_section = section
                self._section_name = section

            def __getitem__(self, item):
                return self._config_section[item]

            def __setitem__(self, item, value):
                self._config_section[item] = value

            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError("config section '%s' has no attribute '%s'" %
                                         (self._section_name.name, key,))

        try:
            proxy = Proxy(self[key])
        except KeyError:
            raise AttributeError("config has no attribute '%s'" % key)

        return proxy

    def save(self, config_file):
        """Save Configuration file.

        Args:
            config_file (str): Path / Location to configuration file.
        """
        with open(config_file, 'w') as f:
            self.write(f)

    def getjson(self, section, option, fallback=None):
        """Load JSON object from value.

        Args:
            section (str): section name.
            option (str): option name.

        Kwargs:
            fallback: Dict or List.

        Returns dict or list.
        """
        try:
            val = self.get(section, option)
            if val.strip() == '' and fallback is not None:
                return fallback
            elif val.strip() == '':
                raise configparser.NoSectionError(section) from None
        except configparser.NoSectionError as e:
            if fallback is not None:
                return fallback
            else:
                raise configparser.NoSectionError(section) from None
        except configparser.NoOptionError as e:
            if fallback is not None:
                return fallback
            else:
                raise configparser.NoOptionError(section, option) from None

        try:
            return js.loads(val)
        except json.decoder.JSONDecodeError as e:
            raise configparser.ParsingError("section '%s'" % section +
                                            " option '%s'" % option +
                                            " (JSON %s)" % e) from None

    def getlist(self, section, option, fallback=None):
        """Get list from option value.

        Example:

        .. code::

            [Bar]
            files_to_check =
                /path/to/file1,
                /path/to/file2,
                /path/to/another file with space in the name

        Args:
            section (str): section name.
            option (str): option name.

        Kwargs:
            fallback (list): List of default values.

        Returns list.
        """
        try:
            val = self.get(section, option)
            if val.strip() == '':
                return []
            val = val.replace('\n','').replace('\r','').split(',')
        except configparser.NoSectionError as e:
            if fallback is not None:
                val = fallback
            else:
                raise configparser.NoSectionError(section) from None
        except configparser.NoOptionError as e:
            if fallback is not None:
                val = fallback
            else:
                raise configparser.NoOptionError(section, option) from None

        if isinstance(val, list):
            return val
        else:
            raise configparser.ParsingError("section '%s'" % section +
                                            " option '%s'" % option +
                                            " expected list") from None

    def kwargs(self, section):
        """Get dict for kwargs for section.

        Excludes all default values.

        Convieniantly use with \*\*kwargs from configuration as arguements.

        Args:
            section (str): section name.

        Returns dict.
        """
        try:
            return self._sections[section]
        except KeyError:
            raise configparser.NoSectionError(section) from None

