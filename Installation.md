# PyWEED Installation

PyWEED is most reliably installed using [conda](https://conda.io/docs/):

```
conda install -c conda-forge pyweed
```

For best results, create a dedicated environment (see [Miniconda](#miniconda) below):

```
conda create -n pyweed -c conda-forge python=3.11 pyweed
```

It can also be installed via pip, although you may need system libraries for some dependencies:

```
pip install pyweed
```

## Issues

Some troubleshooting information can be found in [Support](Support.md).

### Not compatible with Python 3.12

Currently (2024-07-26) PyWEED cannot run under Python 3.12, due to unavailable dependencies. You can create a Python 3.11 environment in `conda` with:

```
conda create -n pyweed -c conda-forge python=3.11
```

### Mac silicon (osx_arm64) requires intel compatible mode

Currently (2024-07-26) PyWEED is not available in the conda-forge `osx-arm64` channel. You can create an environment tied to the (working) `osx-64` channel like:

```
conda create -n pyweed -c conda-forge --subdir osx-64 python=3.11
```

## Running PyWEED

PyWEED installs a `pyweed` script, so from the command line:

```
pyweed
```

## Other installation topics

### Clickable Application

**Mac/Windows only**

This produces a small application that will launch PyWEED when clicked, suitable for adding to your Desktop
or launch bar.

```
pyweed_build_launcher
```

This generates an application launcher -- `PyWEED.app` on Mac or `PyWEED.bat` on Windows -- that can be moved around and double-clicked.

### Miniconda

This is a Python package manager. Miniconda is a lighter version of Anaconda, and is recommended.

**[Miniconda Installers](https://conda.io/miniconda.html)**

(**NOTE** PyWEED requires **Python 3.11** or below!)

**Mac/Linux**: the installation process should put the `conda` command in your shell `PATH`.  
**Windows**: launch the Anaconda Prompt application installed by Miniconda for the next steps.

You can

```
conda create -n pyweed -c conda-forge pyweed
```

This creates a `pyweed` [environment](https://conda.io/docs/using/envs.html) in Anaconda, and installs Python 3, PyWEED,
and all associated dependencies from [conda-forge](https://github.com/conda-forge/) into that environment.

### Network Install

**Mac/Linux only**

This command should perform a complete installation:

```
bash <(curl -Ss https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/install.sh)
```

This downloads and runs a script that builds a conda environment and installs PyWEED into it. Note that this may auto-install various dependencies.

### Source Code

Clone the PyWEED repository with:

```
git clone https://github.com/iris-edu/pyweed.git
```

or [download as a zip file](https://github.com/iris-edu/pyweed/archive/master.zip) and unzip into a `pyweed` directory.

```
cd pyweed
python run_pyweed.py
```
