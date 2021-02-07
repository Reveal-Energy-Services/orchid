#  Copyright 2017-2021 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

"""This module contains functions for converting between instances of the (Python) `Measurement` class and
instances of .NET classes like `UnitsNet.Quantity` and `DateTime`."""


import datetime

import dateutil.tz as duz


# noinspection PyUnresolvedReferences
from System import DateTime, DateTimeKind


class NetQuantityTimeZoneError(ValueError):
    """
    Raised when an error occurs accessing the `TimeZoneInfo` of a .NET `DateTime` instance.
    """
    pass


class NetQuantityLocalDateTimeKindError(NetQuantityTimeZoneError):
    """
    Raised when the `DateTime.Kind` property of a .NET `DateTime` instance is `DateTimeKind.Local`.
    """
    def __init__(self, net_time_point):
        """
        Construct an instance from a .NET DateTime point in time.

        Args:
            net_time_point: A .NET DateTime representing a specific point in time.
        """
        super().__init__(self, '.NET DateTime.Kind cannot be Local.', net_time_point.ToString("O"))


class NetQuantityUnspecifiedDateTimeKindError(NetQuantityTimeZoneError):
    """
    Raised when the `DateTime.Kind` property of a .NET `DateTime` instance is not recognized.
    """
    ERROR_PREFACE = '.NET DateTime.Kind is unexpectedly Unspecified.'

    ERROR_SUFFIX = """
    Although .NET DateTime.Kind should not be Unspecified, it may be
    safe to ignore this error by catching the exception.

    However, because it unexpected, **please** report the issue to
    Reveal Energy Services. 
    """

    def __init__(self, net_time_point):
        """
        Construct an instance from a .NET DateTime point in time.

        Args:
            net_time_point: A .NET DateTime representing a specific point in time.
        """
        super().__init__(self, NetQuantityUnspecifiedDateTimeKindError.ERROR_PREFACE,
                         net_time_point.ToString("O"), NetQuantityUnspecifiedDateTimeKindError.ERROR_SUFFIX)


class NetQuantityNoTzInfoError(NetQuantityTimeZoneError):
    """
    Raised when the `DateTime.Kind` property of a .NET `DateTime` instance is `DateTimeKind.Unspecified`.
    """
    def __init__(self, time_point):
        """
        Construct an instance from a Python point in time.

        Args:
            time_point: A Python `datetime.datetime` representing a specific point in time.
        """
        super().__init__(self, f'The Python time point must specify the time zone.', time_point.isoformat())


def as_datetime(net_time_point: DateTime) -> datetime.datetime:
    """
    Convert a .NET `DateTime` instance to a `datetime.datetime` instance.

    Args:
        net_time_point: A point in time of type .NET `DateTime`.

    Returns:
        The `datetime.datetime` equivalent to the `net_time_point`.
    """
    if net_time_point.Kind == DateTimeKind.Utc:
        return datetime.datetime(net_time_point.Year, net_time_point.Month, net_time_point.Day,
                                 net_time_point.Hour, net_time_point.Minute, net_time_point.Second,
                                 net_time_point.Millisecond * 1000, duz.UTC)

    if net_time_point.Kind == DateTimeKind.Unspecified:
        raise NetQuantityUnspecifiedDateTimeKindError(net_time_point)

    if net_time_point.Kind == DateTimeKind.Local:
        raise NetQuantityLocalDateTimeKindError(net_time_point)

    raise ValueError(f'Unknown .NET DateTime.Kind, {net_time_point.Kind}.')


def as_net_date_time(time_point: datetime.datetime) -> DateTime:
    """
    Convert a `datetime.datetime` instance to a .NET `DateTime` instance.

    Args:
        time_point: The `datetime.datetime` instance to covert.

    Returns:
        The equivalent .NET `DateTime` instance.
    """
    if time_point.tzinfo != duz.UTC:
        raise NetQuantityNoTzInfoError(time_point)

    return DateTime(time_point.year, time_point.month, time_point.day, time_point.hour, time_point.minute,
                    time_point.second, microseconds_to_integral_milliseconds(time_point.microsecond),
                    DateTimeKind.Utc)


def microseconds_to_integral_milliseconds(to_convert: int) -> int:
    """
    Convert microseconds to an integral number of milliseconds.

    Args:
        to_convert: The milliseconds to convert.

    Returns:
        An integral number of milliseconds equivalent to `to_convert` microseconds.

    """
    return int(round(to_convert / 1000))


__all__ = (
    # Module exceptions
    NetQuantityTimeZoneError,
    NetQuantityLocalDateTimeKindError,
    NetQuantityNoTzInfoError,
    NetQuantityUnspecifiedDateTimeKindError,

    # Module methods
    as_datetime,
    as_net_date_time,
)
