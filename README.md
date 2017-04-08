# PyWEED

PyWEED is a cross-platform downloadable app for retrieving event-based seismic data

# Application Binaries

_Highly Experimental!_

Mac OS X: http://ds.iris.edu/files/jweed/PyWEED-1.1.dmg

# Anaconda

It's far more reliable to run PyWEED from an [Anaconda](https://docs.continuum.io/anaconda/) environment.

If you don't have Anaconda installed, download it or [miniconda](http://conda.pydata.org/miniconda.html) and follow the [Quick Install](http://conda.pydata.org/docs/install/quick.html)
instructions.

The installation process should put the `conda` command in your shell `PATH`.

## Get the PyWEED project

Download a [release](https://github.com/iris-edu/pyweed/releases) and unpack it.

Or use Git:

```
git clone https://github.com/iris-edu/pyweed.git
cd pyweed
```

## Create an environment

The packages necessary to run PyWEED are defined in the `environment.yml` file in the root of the project.

From the root directory, run:

`conda env create`

This will create an environment named `pyweed` in your Anaconda system. You can activate this environment by running:

`source activate pyweed`

You can return to the default Anaconda environment by running:

`source deactivate`

## Running the PyWEED GUI

The code is in the `pyweed` subdirectory.

```
cd pyweed
python pyweed_gui.py
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

