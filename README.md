# pyweed

PyWEED is a cross-platform downloadable app for retrieving event-based seismic data

# Installation

The [Anaconda](https://docs.continuum.io/anaconda/) package manager is by far the 
easiest way to install the packages and resources need for Pyweed. Begin by downloading
[miniconda](http://conda.pydata.org/miniconda.html) for python 2.7 for your operating
system and then follow the [Quick Install](http://conda.pydata.org/docs/install/quick.html)
instructions.

The installation process should put the `conda` command in your shell `PATH`. If you have
multiple instances of Anaconda installed, you may need to tweak some of the following commands
to include the specific path to the newly installed version (labeled as `$CONDA_PATH` below).

## Get the PyWEED project

You can use Git to download the project:

```
git clone https://github.com/iris-edu-int/pyweed.git
cd pyweed
```

## Creating a Python environment

The packages necessary to run PyWEED are defined in the `environment.yml` file in the root of the project.

From the root directory, run:

`conda env create`  
or  
`$CONDA_PATH/bin/conda env create`

This will create an environment named `pyweed` in your Anaconda system. You can activate this environment by running:

`source activate pyweed`  
or  
`source $CONDA_PATH/bin/activate pyweed`

You can return to the default Anaconda environment by running:

`source deactivate`  
or  
`source $CONDA_PATH/bin/deactivate`

# Running the PyWEED GUI

The code is in the `pyweed` subdirectory.

```
cd pyweed
python pyweed_gui.py
```

# Running PyWEED without a GUI

**Note** this is a work in progress

```pycon
>>> from pyweed import PyWeed
>>> pyweed = PyWeed()
2017-02-17 14:28:36 - INFO - pyweed - Logging configured
2017-02-17 14:28:36 - INFO - pyweed - Loading preferences
2017-02-17 14:28:36 - DEBUG - pyweed - Set event options: {'time_choice': 'timeBetween', 'mindepth': '0.0', 'maxlongitude': '180.0', 'maxdepth': '6800.0', 'location_choice': 'locationDistanceFromPoint', 'minlatitude': '-90.0', 'minlongitude': '-180.0', 'maxlatitude': '90.0', 'minmagnitude': '5.0', 'maxmagnitude': '10.0', 'longitude': '30.0', 'starttime': '2017-01-14T23:51:47', 'latitude': '50.0', 'endtime': '2017-02-13T23:51:47', 'maxradius': '50.0', 'minradius': '0.0'}
2017-02-17 14:28:36 - DEBUG - pyweed - Set station options: {'time_choice': 'timeFromEvents', 'longitude': '0.0', 'maxlongitude': '180.0', 'maxlatitude': '90.0', 'location_choice': 'locationFromEvents', 'minlatitude': '-90.0', 'minlongitude': '-180.0', 'network': '_GSN', 'station': '*', 'location': '*', 'starttime': '2017-01-14T23:51:49', 'latitude': '0.0', 'endtime': '2017-02-13T23:51:49', 'maxradius': '30.0', 'channel': 'BHZ', 'minradius': '0.0'}
2017-02-17 14:28:36 - INFO - pyweed - Checking on download directory...
2017-02-17 14:28:36 - DEBUG - pyweed_utils - Removed 0 files to keep /Users/adam/.pyweed_downloads below 10 megabytes
2017-02-17 14:28:36 - INFO - pyweed - Creating ObsPy client for IRIS
>>> pyweed.event_options
{'time_choice': 'timeBetween', 'mindepth': 0.0, 'longitude': 30.0, 'maxlongitude': 180.0, 'endtime': UTCDateTime(2017, 2, 13, 23, 51, 47), 'location_choice': 'locationDistanceFromPoint', 'minlatitude': -90.0, 'maxlatitude': 90.0, 'minmagnitude': 5.0, 'maxmagnitude': 10.0, 'maxdepth': 6800.0, 'starttime': UTCDateTime(2017, 1, 14, 23, 51, 47), 'latitude': 50.0, 'minlongitude': -180.0, 'maxradius': 50.0, 'minradius': 0.0}
>>> pyweed.fetch_events()
2017-02-17 14:28:55 - INFO - pyweed - Set events
>>> print pyweed.events
20 Event(s) in Catalog:
2017-02-12T13:48:15.660000Z | +39.600,  +26.092 | 5.2 Mwr
2017-02-10T15:01:49.620000Z | +74.337,  -92.487 | 5.2 mb
...
2017-01-18T10:25:25.480000Z | +42.584,  +13.197 | 5.6 Mww
2017-01-18T09:25:41.600000Z | +42.659,  +13.209 | 5.3 Mww
To see all events call 'print(CatalogObject.__str__(print_all=True))'
```

# Configuration

When PyWEED starts up it searches for configuration information in `~/.pyweed/config.ini`.

This human editable configuration information can be used to override the default settings
associated with the map and the Event and Station Options dialogues. For example, you can
change the map projection with the following modification to config.ini:

```
[Map]
projection = cyl
```

Please see the (TODO documentation) for a list of all configurable options.

# Developer resources:

 * http://zetcode.com/gui/pyqt4/introduction/

