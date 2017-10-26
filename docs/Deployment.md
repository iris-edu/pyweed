# Deployment

These are instructions for releasing a new version of PyWEED to [conda-forge](https://conda-forge.org/).

Some helpful links:  
https://packaging.python.org/tutorials/distributing-packages/  
https://docs.anaconda.com/docs_oss/conda/building/bpp

This process requires installing some additional conda packages:

```
conda install conda-build
conda install twine
```

## 1. Update the version

The version is set in `pyweed/__init__.py`.

This should follow the 
[Python Semantic Versioning](https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred)
scheme.

## 2. Build and deploy to PyPi

From the top-level path in the project:

```
python setup.py sdist
```

This will create a versioned distribution in the `dist/` subdirectory, ie. `dist/pyweed-0.5.5.tar.gz`.

Upload to PyPi with:

```
twine upload dist/pyweed-0.5.5.tar.gz
```

You should see the new version listed on the PyPi page: https://pypi.org/project/pyweed/#history

Find the download page for the new version; this should have a __sha256__ value which you will need for the next step.

## 3. Update the conda-forge recipe

Follow the instructions here: https://conda-forge.org/#update_recipe

You will need to fork a GitHub project, make changes, then submit a pull request to apply your changes.

The version is defined at the top of the `meta.yaml` file:

```
{% raw %}
{% set name = "pyweed" %}
{% set version = "0.5.2.dev0" %}
{% set sha256 = "3e1e8e35cba3f09a52a540b4351042d9e62a98bc430d7f70315df621fb2177f1" %}
{% endraw %}
```

Change *version* to match the new version number.
Update the *sha256* value with the checksum value from the PyPi download page (ie. https://pypi.org/project/pyweed/0.5.2.dev0/#files)

### Test Build

```
conda build -c conda-forge --python 3.5 [path containing meta.yaml]
```

For example, if `meta.yaml` is at `recipe/meta.yaml` you would say:

```
conda build -c conda-forge --python 3.5 recipe
```

Near the end, it should say where the built package can be found, eg.

    TEST END: /workspace/anaconda/conda-bld/osx-64/pyweed-0.5.2.dev1-py35hf6ed582_0.tar.bz2

### Test Install

You can install the test build locally as well.

First, create a new environment based on the recipe requirements. (You shouldn't have to do this, but you do; see https://github.com/conda/conda/issues/466)

ie. if the recipe says

```
requirements:
  run:
    - python
    - obspy
    - pyqt 4.11*
    - qtconsole
    - basemap
    - pyproj
    - pillow
```

Create a "pyweed-temp" environment like

```
conda create -n pweed-temp python=3.5 obspy pyqt=4.11 qtconsole basemap pyproj pillow
```

(Giving the version `python=3.5` here, along with the `--python 3.5` bit above, are to ensure that Python 3 is used.)

Then activate the environment

```
source activate pyweed-temp
```

Now install the local package:

```
conda install /workspace/anaconda/conda-bld/osx-64/pyweed-0.5.2.dev1-py35hf6ed582_0.tar.bz2
```

The `pyweed` executable should be in your PATH:

```
$ which pyweed
/workspace/anaconda/envs/pyweed-test/bin/pyweed
```

## 4. Submit the updated recipe

Check in the changes and submit a pull request to the `conda-forge` repo. This will build and test the changes, and upon successful completion the new version will be made available.
