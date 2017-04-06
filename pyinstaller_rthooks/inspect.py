# Override inspect.getfile which doesn't work in PyInstaller
import inspect
import os.path
import logging

_old_getfile = inspect.getfile

def _getfile(object):
    if inspect.isframe(object):
        try:
            file = object.f_globals['__file__']
            print("inspect.getfile returning %s" % file)
            return file
        except:
            pass
    return _old_getfile(object)

inspect.getfile = _getfile
