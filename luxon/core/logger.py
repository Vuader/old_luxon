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
import sys
import logging
import logging.handlers
import threading

from luxon import g
from luxon.exceptions import NoContextError
from luxon.structs.threadlist import ThreadList
from luxon.core.cls.singleton import NamedSingleton
from luxon.utils.formatting import format_ms
from luxon.utils.files import is_socket
from luxon.utils.split import list_of_lines, split_by_n
from luxon.utils.encoding import is_text, if_bytes_to_unicode


log_format = logging.Formatter('%(asctime)s%(app_name)s'
                               ' %(name)s[%(pid)s]' +
                               ' <%(levelname)s>: %(message)s %(request)s',
                               datefmt='%b %d %H:%M:%S')

_cached_root_configured = False

_cached_loggers = []

def log_formatted(logger_facility, message, prepend=None, append=None):
    """Using logger log formatted content

    Args:
        logger_facility (object): Python logger. (log.debug for example)
        content (str): Message to log.
    """
    if len(message) > 0:
        _message = list_of_lines(message)
        message = []
        for line in _message:
            # Safe Limit per message...
            # There is resrictions on message sizes.
            # https://tools.ietf.org/html/rfc3164
            # https://tools.ietf.org/html/rfc5426
            message += split_by_n(line, 500)

        if len(message) > 1:
            for l, p in enumerate(message):
                if prepend is not None:
                    msg = '%s %s# %s' % (prepend, l, p)
                else:
                    msg = '%s# %s' % (l, p)

                if append is not None:
                    msg = '%s %s' % (msg, append)

                logger_facility(msg)
        else:
            if prepend is not None:
                msg = '%s %s' % (prepend, message[0])
            else:
                msg = '%s' % message[0]

            if append is not None:
                msg = '%s %s' % (msg, append)

            logger_facility(msg)

def set_level(logger_or_handler, level):
    try:
        level = int(level)
    except ValueError:
        level = level.upper().strip()
        if level in ['CRITICAL',
                     'ERROR',
                     'WARNING',
                     'INFO',
                     'DEBUG']:
            logger_or_handler.setLevel(getattr(logging, level))
        else:
            raise ValueError("Invalid logging level '%s'" % level +
                             " for logger " +
                             " '%s'" % logger_or_handler.name) from None


class _TachyonFilter(logging.Filter):
    def __init__(self):
        logging.Filter.__init__(self)

    def filter(self, record):
        record.pid = str(os.getpid())
        try:
            if hasattr(g, 'config'):
                record.app_name = ' ' + g.config.application.name
            else:
                record.app_name = ''
        except NoContextError:
            record.app_name = ''
        try:
            request = g.current_request.log
            record.request = " ".join(['(%s: %s)' % (key, value) \
                        for (key, value) in request.items()])
        except NoContextError:
            record.request = ''

        return True

def format_timer(elapsed):
    """Format Float / Int for second duruation.

    Args:
        elapsed (int/float): Elapsed float/int

    Return formatted time str.
    """
    import datetime
    if elapsed is not None:
        return ' (DURATION: %s)' % format_ms(elapsed)

    else:
        return ''

def format_msg(msg):
    """Format Message.

    Ensure message is str and not binary data.
    """
    if is_text(msg):
        return if_bytes_to_unicode(msg)
    else:
        if isinstance(msg, bytes):
            return 'BINARY BYTES'
        else:
            return str(msg)

class GetLogger(metaclass=NamedSingleton):
    """Wrapper Class for convienance.

    Args:
        name (str): Typical Module Name, sub-logger name, (optional)

    Ensures all log output is formatted correctly.
    """
    __slots__ = ('handlers',
                 'name',
                 'logger',
                 '_cached_effective_level')

    def __init__(self, name=None):
        self.handlers = {}
        self.name = name
        self.logger = logging.getLogger(name)
        self._cached_effective_level = self.logger.getEffectiveLevel()

        self.app_configure()

        if name is None:
            name = 'root'

        self.info("Started Logger '%s'" % name)
        _cached_loggers.append(self)

    def app_configure(self):
        global _cached_root_configured

        if self.name is None:
            name = 'application'
        else:
            name = self.name

        try:
            if hasattr(g, 'config') and name in g.config:
                section = g.config[name]
                # SET LOG LEVEL FOR GLOBAL or MODULE
                self.setLevel(section.get('log_level', fallback='DEBUG'))

                # ENABLE STDOUT FOR GLOBAL or MODULE
                if section.getboolean('log_stdout', fallback=False):
                    self.log_stdout()
                else:
                    self.no_stdout()

                # ENABLE SYSLOG FOR GLOBAL OR MODULE
                log_server = section.get('log_server', fallback=None)
                if log_server is not None:
                    log_server_port = section.get('log_server_port', fallback=514)
                    self.log_syslog(log_server, log_server_port)

                # ENABLE FILE LOG FOR GLOBAL OR MODULE
                log_file = section.get('log_file', fallback=None)
                if log_file is not None:
                    self.log_file(log_file)

                if name == 'application':
                    _cached_root_configured = True
        except NoContextError:
            pass



        return self

    def _check_root_configured(self):
        global _cached_root_configured

        ### Enable Default Logging stdout.
        if self.name is not None:
            root = GetLogger()
        else:
            root = self

        if len(root.handlers) == 0:
            root.setLevel('ERROR')
            root.log_stdout()

        _cached_root_configured = True

    def setLevel(self, level):
        set_level(self.logger, level)
        self._cached_effective_level = self.logger.getEffectiveLevel()
        for logger in _cached_loggers:
            logger._cached_effective_level = None


    def _log(self, handler, log_level=logging.NOTSET):
        set_level(handler, log_level)
        handler.setFormatter(log_format)
        handler.addFilter(_TachyonFilter())
        self.logger.addHandler(handler)


    def _no(self, name):
        if name in self.handlers:
            self.logger.removeHandler(self.handlers[name])
            del self.handlers[name]

    def log_file(self, log_file, log_level=logging.NOTSET):
        if 'file' in self.handlers:
            return self.handlers['file']
        else:
            handler = logging.FileHandler(log_file)
            self._log(handler, log_level)
            self.handlers['file'] = handler
            return handler

    def no_file(self):
        self._no('file')

    def log_stdout(self, log_level=logging.NOTSET):
        if 'stdout' in self.handlers:
            return self.handlers['stdout']
        else:
            handler = logging.StreamHandler(stream=sys.stdout)
            self._log(handler, log_level)
            self.handlers['stdout'] = handler
            return handler

    def no_stdout(self):
        self._no('stdout')

    def log_wsgi(self, stream=sys.stderr, log_level=logging.NOTSET):
        self.no_stdout()
        if 'wsgi' in self.handlers:
            return self.handlers['wsgi']
        else:
            handler = logging.StreamHandler(stream=stream)
            self._log(handler, log_level)
            self.handlers['wsgi'] = handler
            return handler

    def no_wsgi(self):
        self._no('wsgi')

    def log_syslog(self, host, port=514, log_level=logging.NOTSET):
        if 'syslog' in self.handlers:
            return self.handlers['syslog']
        else:
            if host == '127.0.0.1' or host.lower() == 'localhost':
                if is_socket('/dev/log'):
                    handler = logging.handlers.SysLogHandler(address='/dev/log')
                elif is_socket('/var/run/syslog'):
                    handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
                else:
                    handler = logging.handlers.SysLogHandler(address=(host, port))
            else:
                handler = logging.handlers.SysLogHandler(address=(host, port))

            self._log(handler, log_level)
            self.handlers['syslog'] = handler
            return handler

    def no_syslog(self):
        self._no('syslog')

    def critical(self, msg, prepend=None, append=None, timer=None):
        """Log Critical Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if _cached_root_configured is False:
            self._check_root_configured()
        if self.getEffectiveLevel() <= logging.CRITICAL:
            msg = format_msg(msg)
            if timer is not None:
                msg += format_timer(timer)
            log_formatted(self.logger.critical, msg, prepend, append)

    def error(self, msg, prepend=None, append=None, timer=None):
        """Log Error Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if _cached_root_configured is False:
            self._check_root_configured()
        if self.getEffectiveLevel() <= logging.ERROR:
            msg = format_msg(msg)
            if timer is not None:
                msg += format_timer(timer)
            log_formatted(self.logger.error, msg, prepend, append)

    def warning(self, msg, prepend=None, append=None, timer=None):
        """Log Warning Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if _cached_root_configured is False:
            self._check_root_configured()
        if self.getEffectiveLevel() <= logging.WARNING:
            msg = format_msg(msg)
            if timer is not None:
                msg += format_timer(timer)
            log_formatted(self.logger.warning, msg, prepend, append)

    def info(self, msg, prepend=None, append=None, timer=None):
        """Log Info Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if _cached_root_configured is False:
            self._check_root_configured()

        if self.getEffectiveLevel() <= logging.INFO:
            msg = format_msg(msg)
            if timer is not None:
                msg += format_timer(timer)
            log_formatted(self.logger.info, msg, prepend, append)

    def debug(self, msg, prepend=None, append=None, timer=None):
        """Log Debug Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Appener value returned using

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if _cached_root_configured is False:
            self._check_root_configured()
        if self.getEffectiveLevel() <= logging.DEBUG:
            msg = format_msg(msg)
            if timer is not None:
                msg += format_timer(timer)
            log_formatted(self.logger.debug, msg, prepend, append)

    def getEffectiveLevel(self):
        """Return effective logging level.

        returns integer
        """
        if self._cached_effective_level is None:
            self._cached_effective_level = self.logger.getEffectiveLevel()

        return self._cached_effective_level

    def debug_mode(self):
        """Returns True if effective level is debug
        """
        if _cached_root_configured is False:
            self._check_root_configured()
        if self.getEffectiveLevel() <= logging.DEBUG:
            return True
        else:
            return False
