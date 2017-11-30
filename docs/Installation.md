# PyWEED Installation

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

These instructions assume a separate [environment](https://conda.io/docs/using/envs.html) for PyWEED;
this is highly recommended, as it will prevent conflicts between PyWEED's support libraries and those for other projects.

```
conda create -n pyweed python=3 pyweed
```

This will create an environment named `pyweed` in your Anaconda system, and install PyWEED and all of its dependencies
into that environment.

# Running PyWEED

## From the command line

To run PyWEED from the command line, you first need to activate the `pyweed` environment.

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

You can launch PyWEED from a Python shell as well. (Be sure you are running the shell within the `pyweed` environment!)

```
from pyweed import pyweed_launcher
pyweed_launcher.launch()
```

## Mac application bundle

On a Mac, you can create an application bundle, which you can then copy into `Applications`.

```
source activate pyweed
pyweed_build_launcher
mv PyWEED.app /Applications/
```

