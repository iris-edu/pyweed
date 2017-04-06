import inspect
import os.path
import gui
import sys

def test2():
    frame = inspect.currentframe()
    directory = inspect.getfile(frame)
    print(directory)
    print(__file__)
    print(gui.__file__)
    print(sys.path[0])
    print(frame.f_globals['__file__'])

def frame():
    return inspect.currentframe()
