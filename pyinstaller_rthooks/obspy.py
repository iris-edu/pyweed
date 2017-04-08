"""
Real-time hooks for obspy
"""
import inspect

_old_getfile = inspect.getfile
def _getfile(object):
    """
    Override inspect.getfile

    A common idiom within Obspy to get a file path of the current code
    (eg. to find a data file in the same package) is
    >>> inspect.getfile(inspect.currentframe())
    This doesn't work in PyInstaller for some reason.

    In every case I've tried, this returns the same thing as __file__,
    which does work in PyInstaller, so this hook tries to return that instead.
    """
    if inspect.isframe(object):
        try:
            file = object.f_globals['__file__']
            # print("inspect.getfile returning %s" % file)
            return file
        except:
            pass
    return _old_getfile(object)
inspect.getfile = _getfile
