from obspy.core.utcdatetime import UTCDateTime
from distutils.util import strtobool
from logging import getLogger
from numbers import Number
from datetime import timedelta

###
# Webservice request library
#
# Example:
#
# class MyRequest(BaseRequest):
#     """
#     Define a particular webservice request
#     """
#     # These are the keys and types that can be passed into the query
#     param_types = {
#         # A generic string parameter
#         'name': WSParam(),
#         # A date, will be put in the query as ISO format
#         'birthday': WSDateParam(),
#     }
#     # Base query url
#     url = 'http://hostname/path/to/query'
#
# req = MyRequest(name='Foo', birthday=datetime.date(1983,5,12))
#
# response = """
# # id | name | message
# 1|Foo|Hi there
# 2|Bar|Yarr
# """
#
# for row in req.get():
#     name = row['name']
#     message = row['message']
#     print '%s says "%s"' % (name, message)
#
# prints = """
# Foo says "Hi there"
# Bar says "Yarr"
# """

LOGGER = getLogger(__name__)


class Option(object):
    """
    Defines a web service query parameter.  This allows the service API to take parameter
    values as Python objects, and convert them to the proper string form for the service.
    """
    def __init__(self, option_name=None, default=None, hidden=False):
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

    @example
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
    """
    def __new__(cls, name, bases, attrs):
        options = {}
        for attr, option in attrs.iteritems():
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


class Options(object):
    """
    Base class for a web service request.
    """

    __metaclass__ = OptionsMeta

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
        @param hidden: include (or not) where Option.hidden is set
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
        return [key for key, option in self._options.items() if hidden or not option.hidden]

    def __setattr__(self, k, v):
        if k in self._options:
            v = self._options[k].to_option(v)
        self.__dict__[k] = v

    def __repr__(self):
        return repr(self.get_options())
