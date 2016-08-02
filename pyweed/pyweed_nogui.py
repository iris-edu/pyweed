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
from stations import Stations

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
    
    
    # Test event query -----------------
    
    parameters = {}        
    parameters['starttime'] = args.starttime
    parameters['endtime'] = args.endtime
    parameters['minmag'] = args.minmag
    parameters['maxmag'] = '10'
        
    eventsHandler = Events()
    eventsDF = eventsHandler.query(parameters=parameters)
    print(eventsDF)
    
    # Test station query ---------------
    
    parameters = {}
    parameters['starttime'] = args.starttime
    parameters['endtime'] = args.endtime
    parameters['network'] = 'IU,UW'
    parameters['station'] = 'A*'
    parameters['location'] = '00'
    parameters['channel'] = '?HZ'
    
    stationsHandler = Stations()
    stationsDF = stationsHandler.query(parameters=parameters)
    print(stationsDF)
    
    
    debug_point = 1


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
