# -*- coding: utf-8 -*-
"""
Helper class for web services.

Options represents a set of key/value pairs (ie. query parameters), internally these are typed values but
they can be read/written as strings.

>>> class Test(Options):
...     option1 = Option()
...     option2 = DateOption()
>>> t = Test()
>>> t.option1 = 'test'
>>> t.option1
'test'
>>> t.option2 = '2012-01-01'
>>> t.option2
UTCDateTime(2012, 1, 1, 0, 0)
>>> t.get_options(stringify=True)
{'option1': 'test', 'option2': '2012-01-01'}

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from obspy.core.utcdatetime import UTCDateTime
from distutils.util import strtobool
from logging import getLogger
from numbers import Number
from datetime import timedelta
from future.utils import with_metaclass

"""
"""

LOGGER = getLogger(__name__)


class Option(object):
    """
    Defines a web service query parameter.  This allows the service API to take parameter
    values as Python objects, and convert them to the proper string form for the service.
    """
    def __init__(self, option_name=None, default=None, hidden=False):
        """
        :param options_name: The name of the option (eg. "starttime")
        :param default: The default to use if no value is set
        :param hidden: Indicate that this option shouldn't be included in the actual query
        """
        self.option_name = option_name
        self.default = default
        self.hidden = hidden

    def to_option(self, value):
        """
        Turn the value into a "native" option type
        """
        return value

    def to_string(self, value):
        return str(value)


class DateOption(Option):
    """
    A date parameter.
    """
    def to_option(self, value):
        # Value can be a number indicating number of days relative to today
        if isinstance(value, Number):
            return UTCDateTime() + timedelta(days=value)
        else:
            return UTCDateTime(value)

    def to_string(self, value):
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, str):
            return value
        else:
            raise ValueError("%s is not a date" % (value,))


class BinaryOption(Option):
    """
    A binary parameter that is passed in a query as "yes" or "no".
    """
    def to_option(self, value):
        return strtobool(value)

    def to_string(self, value):
        return "yes" if value else "no"


class IntOption(Option):
    """
    An integer value
    """
    def to_option(self, value):
        return int(value)


class FloatOption(Option):
    """
    A floating point value
    """
    def to_option(self, value):
        return float(value)


class OptionsMeta(type):
    """
    Metaclass for the Options type, this converts the Options defined in the class attributes
    into type-aware attributes.
    """
    def __new__(cls, name, bases, attrs):
        options = {}
        for attr, option in attrs.items():
            if isinstance(option, Option):
                # Keep the definition
                options[attr] = option
                # Set the actual instance attribute to the default value or None
                if option.default is not None:
                    attrs[attr] = option.to_option(option.default)
                else:
                    attrs[attr] = None
        # Store the option definitions in a private attribute
        attrs['_options'] = options
        return type.__new__(cls, name, bases, attrs)


class Options(with_metaclass(OptionsMeta, object)):
    """
    Base class for a web service request.
    """

    def set_options(self, options):
        """
        Set all the options in the given dictionary
        """
        for k, v in options.items():
            if k in self._options:
                setattr(self, k, v)

    def get_options(self, keys=None, hidden=True, stringify=False):
        """
        Return the options as a dictionary, with a few options
        @param keys: only include the options named
        @param hidden: if True, include options where Option.hidden is set
        @param stringify: convert the option value to a string
        """
        options = {}
        if not keys:
            keys = self.keys(hidden=hidden)
        for attr in keys:
            option = self._options.get(attr)
            if option:
                value = getattr(self, attr, None)
                if value is not None:
                    if stringify:
                        options[attr] = option.to_string(value)
                    else:
                        options[attr] = value
        return options

    def keys(self, hidden=True):
        """
        Return a list of keys

        @param hidden: if True, include options where Option.hidden is set
        """
        return [key for key, option in self._options.items() if hidden or not option.hidden]

    def __setattr__(self, k, v):
        if k in self._options:
            v = self._options[k].to_option(v)
        self.__dict__[k] = v

    def __repr__(self):
        return repr(self.get_options())
