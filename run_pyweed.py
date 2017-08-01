#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple script to run PyWEED from the source code.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)
import os
import sys

if __name__ == "__main__":
    # Add the current path to PYTHONPATH if necessary
    try:
        from pyweed.pyweed_launcher import launch
    except Exception as e:
        sys.path.append(os.path.dirname(__file__))
        from pyweed.pyweed_launcher import launch
    launch()
