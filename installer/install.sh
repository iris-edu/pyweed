if [[ `uname -s` == "Darwin" ]]; then
  export OS="MacOSX"
else
  export OS="Linux"
fi
echo "Identified OS as $OS"

# Run in a temp directory
WORKING_DIR=`mktemp -d`
if (( $? )); then
  # Probably no mktemp, generate a time-based directory name
  WORKING_DIR=`date "+/tmp/pyweed.%s"`
fi
echo "Working in $WORKING_DIR"
mkdir -p "$WORKING_DIR"
cd "$WORKING_DIR"

export ARCH=`uname -m`

CONDA_INSTALL_PATH="$HOME/.pyweed/miniconda"

###
# Install Anaconda if not found

echo "Looking for Anaconda installation"

# Anaconda may have been previously installed but not on the existing path, so add the install
# path to ensure we find it in that case
export PATH="$PATH:$CONDA_INSTALL_PATH/bin"
hash -r

conda info > /dev/null 2>&1
if (( $? )); then
  echo "
Anaconda Python not found, do you want to install it? [yes|no]
[no] >>> "
  read ans
  ANS=`echo "$ans" | tr '[:upper:]' '[:lower:]'`
  if [[ ($ANS != 'yes') && ($ANS != 'y') ]]; then
    echo "Aborting installation"
    exit 1
  fi

  echo "Downloading Miniconda";
  curl -Ss -o miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-${OS}-${ARCH}.sh

  bash miniconda.sh -b -p $CONDA_INSTALL_PATH
  export PATH="$CONDA_INSTALL_PATH/bin:$PATH"
  hash -r
  conda config --set always_yes yes --set changeps1 no
  conda update -q conda

  # Useful for debugging any issues with conda
  conda info -a
else
  echo "Found Anaconda at" `conda info --root`
fi

###
# Create/update the conda environment

conda env list | grep '^pyweed\s' > /dev/null
if (( $? )); then
  echo "No pyweed environment found"
  ENV_ACTION="create"
else
  echo "Found a pyweed environment"
  ENV_ACTION="update"
fi

echo "Working to $ENV_ACTION PyWEED environment"
curl -Ss -o environment.yml https://raw.githubusercontent.com/iris-edu/pyweed/master/installer/environment.yml
conda env $ENV_ACTION
source activate pyweed

###
# Mac .app bundle

if [[ $OS == 'MacOSX' ]]; then
  echo "Creating Mac app bundle"
  hash -r
  pyweed_build_osx
  echo "
Install PyWEED to /Applications folder? [yes|no]
[no] >>> "
  read ans
  ANS=`echo "$ans" | tr '[:upper:]' '[:lower:]'`
  if [[ ($ANS != 'yes') && ($ANS != 'y') ]]; then
    echo "Application is available at $PWD/PyWEED.app"
  else
    # Move the old version out of the way if necessary
    if [ -e "/Applications/PyWEED.app" ]; then
      mv "/Applications/PyWEED.app" "$PWD/PyWEED.prev.app"
      echo "Previous application moved to $PWD/PyWEED.prev.app"
    fi
    mv -f $PWD/PyWEED.app /Applications/
    echo "Installed to /Applications/PyWEED.app"
  fi
fi

echo "Done!"
