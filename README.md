# PyWEED

PyWEED is a cross-platform downloadable app for retrieving event-based seismic data

__This software is still under development and has not been publicly released__

# Quick Install (Mac/Linux)

The easiest way to install is:

```
curl -Ss https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/install.sh | bash
```

This runs a script that essentially does the steps outlined below.

# Anaconda

The best way to run PyWEED is with [Anaconda](https://docs.continuum.io/anaconda/).

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

From the base directory, run:

```
python pyweed_launcher.py
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

# Application Binaries

_Highly Experimental!_

Mac OS X: http://ds.iris.edu/files/jweed/PyWEED-1.1.dmg


