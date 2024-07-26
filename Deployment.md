# Deployment

These are instructions for releasing a new version of PyWEED to [conda-forge](https://conda-forge.org/).

Some helpful links:

- <https://docs.conda.io/projects/conda-build/en/latest/user-guide/tutorials/building-conda-packages.html>
- <https://packaging.python.org/tutorials/distributing-packages/>
- <https://enterprise-docs.anaconda.com/en/latest/data-science-workflows/packages/build.html>

Some additional packages are required:

```
conda install build conda-build twine
```

## 1. Update the version

The version is set in `pyweed/__init__.py`.

This should follow the
[Python Semantic Versioning](https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred)
scheme.

## 2. Build and deploy to PyPi

From the top-level path in the project:

```
python -m build
```

This will create versioned products in the `dist/` subdirectory, ie. `dist/pyweed-1.0.9.tar.gz`.

Upload to PyPi with:

```
twine upload dist/*
```

You should see the new version listed on the PyPi page: <https://pypi.org/project/pyweed/#history>

Find the download page for the new version; this should have a **sha256** value which you will need for the next step.

## 3. Create an updated conda build recipe

The official instructions are here: <https://conda-forge.org/#update_recipe>

NOTE: **This step can take a day or more**, since it has to go through the conda-forge automated builder. It can
also get held up if the conda-forge linter doesn't like something about your changes. Plan accordingly!

### Update the build recipe

Fork the conda-forge feedstock project here: <https://github.com/conda-forge/pyweed-feedstock>

You will modify your forked version, then submit a pull request to push your changes back to the main repo.

The version is defined at the top of the `meta.yaml` file:
{% raw %}

```
{% set name = "pyweed" %}
{% set version = "1.0.9" %}
{% set build_number = 0 %}
{% set sha256 = "6cadc138306134085ef09a979bb788179627b4dfb1dbbd401756076f1db3949d" %}
```

{% endraw %}
Change **version** to match the new version number, and
update the **sha256** value with the value from the PyPi page in the previous step.

### Test Build

```
conda build -c conda-forge [path containing meta.yaml]
```

For example, to build from `recipe/meta.yaml` you would say:

```
conda build -c conda-forge recipe
```

Near the end of a successful build, it should say where the built package can be found, eg.

    TEST END: /workspace/anaconda/conda-bld/osx-64/pyweed-0.5.2.dev1-py35hf6ed582_0.tar.bz2

### Test Install

You can install the test build locally as well.

First, create a new environment based on the recipe requirements.
(You shouldn't have to do this, but you do; see <https://github.com/conda/conda/issues/466>)

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

Create a scratch environment (we'll call it "pyweed-temp"):

```
conda create -n pyweed-temp obspy pyqt=4.11 qtconsole basemap pyproj pillow
```

Then activate the environment:

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

## 4. Update conda-forge

1. Check in the changes to your forked GitHub repo.
2. Submit a pull request to the [base conda-forge repo](https://github.com/conda-forge/pyweed-feedstock).
3. You will need to wait until the automated build and test have succeeded. **This may take a day or so.**
4. At that point, you should be able to approve the pull request.
5. You need to wait _again_ for the finalized packages to be built and uploaded. The easiest option is to watch
   the [package page](https://anaconda.org/conda-forge/pyweed) which shows the latest available version for each
   platform. When the new version is available for all platforms, the release is finished!
