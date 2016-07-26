#!/Users/jonathan/miniconda2/bin/python
# -*- coding: utf-8 -*-
"""
Test program for creating executables with pyinstaller.

HINTS:

Use Anaconda environment for everything -- hence the python 2.7 path above.
Use 'conda update' if packages are already installed.
 
> conda update conda
> conda install anaconda-client
> conda install --channel https://conda.anaconda.org/conda-forge pyinstaller
> conda install --channel https://conda.anaconda.org/conda-forge packaging
> conda install numpy
> conda install pandas

Compile to generate bop1.spec file

> /Users/jonathan/miniconda2/bin/pyinstaller --onefile bop1.py

Modify this line in the bop1.spec file for hidden dependendencies needed for numpy

>              hiddenimports=['six','packaging','packaging.version','packaging.specifiers','packaging.requirements'],

Compile from the .spec file

> /Users/jonathan/miniconda2/bin/pyinstaller --onefile bop1.spec

This produces an OSX executable file with no system dependencies.
"""

# Similar imports to pyweed_gui

from __future__ import (absolute_import, division, print_function)

import sys
import string

import urllib

import numpy as np
import pandas as pd

print("Hello world.")

