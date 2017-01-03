# pyweed

PyWEED is a cross-platform downloadable app for retrieving event-based seismic data

*(version 0.0.9)*

# Installation

The [Anaconda](https://docs.continuum.io/anaconda/) package manager is by far the 
easiest way to install the packages and resources need for Pyweed. Begin by downloading
[miniconda](http://conda.pydata.org/miniconda.html) for python 2.7 for your operating
system and then follow the [Quick Install](http://conda.pydata.org/docs/install/quick.html)
instructions.

## Installing conda

`bash ~/Downloads/Miniconda2-latest-MacOSX-x86_64.sh`

Accept all defaults and just hit spacebar when you see a `:` prompt while reviewing the license.

This should install the Anaconda environment, and update the `PATH` in your `~/.bash_profile` so that this is the version of Python that is run by default:

```
# added by Miniconda2 4.1.11 installer
export PATH="/Users/jonathan/miniconda2/bin:$PATH"
```

If you now `source ~/.bash_profile` you will get conda and the Anaconda version of python by default.
The first thing to do is update conda itself:

`conda update conda`

## Creating a Python environment

The packages necessary to run PyWEED are defined in the `environment.yml` file in the root of the project.

From the root directory, run:

`conda env create`

This will create an environment named `pyweed` in your Anaconda system. You can activate this environment by running:

`source activate pyweed`

You can return to the default Anaconda environment by running:

`source deactivate`

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

