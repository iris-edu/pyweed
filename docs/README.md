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

The installation process should put the `conda` command in your shell `PATH`.

### Install the PyWEED environment

[Anaconda environments](https://conda.io/docs/using/envs.html) allow different projects to each have their own
version of Python and various dependencies.

Download the PyWEED environment definition from https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/environment.yml

Then run:

`conda env create -f environment.yml`

This will create an environment named `pyweed` in your Anaconda system, and install PyWEED and all of its dependencies
into that environment.

### Create a clickable app (Mac only)

On Mac, you can create a clickable app bundle, which you can then copy into `Applications`.

```
source activate pyweed
pyweed_build_launcher
mv PyWEED.app /Applications/
```

You can then launch this instead of using the command line (described below) to run PyWEED.

# Running PyWEED

You can run PyWEED from the command line by activating the `pyweed` environment, then running the `pyweed` command:

```
source activate pyweed
pyweed
```

__In Windows__ the activation command is slightly different:

```
activate pyweed
pyweed
```

## Running from Python

You can launch PyWEED from a Python shell as well. Be sure you are running the shell within the `pyweed` environment.

```
from pyweed import pyweed_launcher
pyweed_launcher.launch()
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
