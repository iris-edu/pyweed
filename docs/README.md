# PyWEED

PyWEED is a cross-platform downloadable app for retrieving event-based seismic data

__This software is still under development and has not been publicly released__

Send comments/problems to adam@iris.washington.edu.

## Bash Install (Mac/Linux only)

On Mac and Linux, this command should perform a complete installation:

```
bash <(curl -Ss https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/install.sh)
```

This runs a script that essentially performs the steps outlined in the Conda Install below.

## Conda Install (Mac/Linux/Windows)

### Install Conda if needed

If you don't have [Conda](https://conda.io/docs/) installed already, we recommend using [Miniconda](https://conda.io/miniconda.html).

__[Miniconda Installers](https://conda.io/miniconda.html)__

__PyWEED requires Python 3.5 or higher!__

The installation process should put the `conda` command in your shell `PATH`.

### Install PyWEED

For a simple install:

```
conda install -c conda-forge pyweed
```

If you use conda for other projects, it is much more reliable to create a separate 
[environment](https://conda.io/docs/using/envs.html) for PyWEED; this will prevent conflicts between PyWEED's
support libraries and those for other projects.

```
conda create -n pyweed python=3 pyweed
```

This will create an environment named `pyweed` in your Anaconda system, and install PyWEED and all of its dependencies
into that environment.

# Running PyWEED

If you created a separate environment for PyWEED, activate that first:

```
source activate pyweed
```

Or on Windows:

```
activate pyweed
```

Then you can run PyWEED from the command line:

```
pyweed
```

## Running from Python

You can launch PyWEED from a Python shell as well. Be sure you are running the shell within the `pyweed` environment.

```
from pyweed import pyweed_launcher
pyweed_launcher.launch()
```

## Mac application bundle

On Mac, you can create a clickable app bundle, which you can then copy into `Applications`.

```
source activate pyweed
pyweed_build_launcher
mv PyWEED.app /Applications/
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
