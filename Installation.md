# PyWEED Installation

PyWEED is distributed as an [anaconda](https://conda.io/docs/) package.

Some troubleshooting information can be found in [Support](Support.md).

## Install Anaconda/Miniconda (if needed)

This is the conda package manager. Miniconda is a lighter version of Anaconda, and is recommended.

__[Miniconda Installers](https://conda.io/miniconda.html)__

This page includes both 2.x and 3.x versions, it's better to get the 3.x version. (It doesn't strictly matter, though.)

__Mac/Linux__: the installation process should put the `conda` command in your shell `PATH`.  
__Windows__: launch the Anaconda Prompt application installed by Miniconda for the next steps.

## Install PyWEED

Run the following command:

```
conda create -n pyweed -c conda-forge python=3 pyweed
```

This creates a `pyweed` [environment](https://conda.io/docs/using/envs.html) in Anaconda, and installs Python 3, PyWEED,
and all associated dependencies from [conda-forge](https://github.com/conda-forge/) into that environment.

# Running PyWEED

__Mac/Linux__

```
source activate pyweed
pyweed
```

__Windows__ (from the Anaconda Prompt)

```
activate pyweed
pyweed
```

# Other Options

## Network Install

__Mac/Linux only__

This command should perform a complete installation:

```
bash <(curl -Ss https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/install.sh)
```

This downloads and runs a script that essentially performs the steps outlined above.

## Clickable Application

__Mac/Windows only__

This produces a small application that will launch PyWEED when clicked, suitable for adding to your Desktop
or launch bar.

__Mac__

```
source activate pyweed
pyweed_build_launcher
mv PyWEED.app /Applications/
```

__Windows__

```
activate pyweed
pyweed_build_launcher
move PyWEED.bat Desktop
```
