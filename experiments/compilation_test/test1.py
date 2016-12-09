#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test program for creating executables with pyinstaller.

HINTS:

 
> conda update conda
> conda install anaconda-client
> conda install --channel https://conda.anaconda.org/conda-forge pyinstaller

Compile to generate test1.spec file

> pyinstaller --onefile test1.py

Modify this line in the test1.spec file for hidden dependendencies needed for numpy

>              hiddenimports=['six','packaging','packaging.version','packaging.specifiers','packaging.requirements'],

Compile from the .spec file

> pyinstaller --onefile test1.spec

This produces an OSX executable file with no system dependencies.
"""

print("Hello world.")

