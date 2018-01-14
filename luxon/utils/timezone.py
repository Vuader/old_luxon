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
from datetime import datetime as py_datetime
from datetime import tzinfo, timedelta

import pytz
from tzlocal import get_localzone

from luxon import g
from luxon import GetLogger

log = GetLogger(__name__)

_cached_time_zone_system = None

def parse_http_date(http_date, obs_date=False):
    """Converts an HTTP date string to a datetime instance.

    Args:
        http_date (str): An RFC 1123 date string.
            e.g. Tue, 15 Nov 1994 12:45:26 GMT

    Keyword Arguments:
        obs_date (bool): Support obs-date formats according to
            RFC 7231. (Default False)
            e.g. Sunday, 06-Nov-94 08:49:37 GMT

    Returns:
        datetime: A UTC datetime instance corresponding to the given
        HTTP date.

    Raises:
        ValueError: http_date doesn't match any of the available time formats
    """

    if not obs_date:
        return py_datetime.strptime(http_date, '%a, %d %b %Y %H:%M:%S %Z')

    time_formats = (
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d-%b-%Y %H:%M:%S %Z',
        '%A, %d-%b-%y %H:%M:%S %Z',
        '%a %b %d %H:%M:%S %Y',
    )

    for time_format in time_formats:
        try:
            return py_datetime.strptime(http_date, time_format)
        except ValueError:
            continue

    raise ValueError('time data %r does not match known formats' % http_date)


class TimezoneGMT(tzinfo):
    """GMT timezone class implementing GMT Timezone"""

    UTC_OFFSET = timedelta(hours=0)
    DST_OFFSET = timedelta(hours=0)
    NAME = 'GMT'

    def utcoffset(self, dt):
        """Get the offset from UTC.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: Offset.
        """

        return self.UTC_OFFSET

    def tzname(self, dt):
        """Get the name of this timezone.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            str: e.g. "GMT"
        """

        return self.NAME

    def dst(self, dt):
        """Return the daylight saving time (DST) adjustment.

        GMT has no daylight savings time. Always Zero.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: DST adjustment for GMT.
        """
        return self.DST_OFFSET

class TimezoneUTC(TimezoneGMT):
    """UTC timezone class implementing UTC Timezone"""
    TZNAME = 'UTC'

def TimezoneSystem():
    global _cached_time_zone_system

    if _cached_time_zone_system is None:
        _cached_time_zone_system = get_localzone()

    return _cached_time_zone_system

def TimezoneApp():
    global _cached_time_zone_app

    if _cached_time_zone_app is None:
        app_timezone = g.app.config.get('application',
                                                'timezone')
        _cached_time_zone_app = pytz.timezone(app_timezone)
        # TODO IF FAILS LOG AND FALL BACK TO SYSTEM

    return _cached_time_zone_app

def to_timezone(datetime, dst=TimezoneSystem(), src=None):
    if src is None and datetime.tzinfo is None:
        raise ValueError('to_timezone not possible from naive datetime' +
                         ' use src keyword to define source timezone')
    if isinstance(dst, str):
        dst = pytz.timezone(dst)
    if src is not None:
        if isinstance(src, str):
            src = pytz.timezone(src)
        datetime = datetime.replace(tzinfo=src)

    datetime = datetime.astimezone(tz=dst)
    return dst.normalize(datetime)

def now(tz=TimezoneUTC()):
    """Current date time.

    Keyword Args:
        tz (tzinfo): Timezone Object. Defaults to UTC.
    """
    return py_datetime.now(tz=tz)

def to_utc(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneUTC(), src=None)

def to_gmt(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneGMT(), src=None)

def to_system(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneSystem(), src=None)

def to_app(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneApp(), src=None)

def parse(datetime):
    # TODO
    raise NotImplemented('TODO')

    if isinstance(datetime, py_datetime):
        return datetime
