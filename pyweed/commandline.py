#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Testing function."""

from __future__ import (absolute_import, division, print_function)

# Basic modules
import os
import sys
import argparse
import datetime

# pyweed modules
from events import Events

__version__ = "0.0.1"


def main():

    # Parse arguments ----------------------------------------------------------
    
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('--starttime', action='store', required=True,
                        help='starttime in ISO 8601 format')
    parser.add_argument('--endtime', action='store', required=False,
                        help='endtime in ISO 8601 format')
    parser.add_argument('-M', '--minmag', required=True,
                        help='minimum magnitue')

    args = parser.parse_args(sys.argv[1:])
    
    
    # Test code
    
    events = Events()
    
    events.query(starttime=args.starttime,
                 endtime=args.endtime,
                 minmag=args.minmag)
    
    df = events.get_df()
    
    print(df)
    
    debug_point = 1


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
