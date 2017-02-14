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

# Running PyWEED

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

