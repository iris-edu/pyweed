if [[ `uname -s` == "Darwin" ]]; then
  export OS="MacOSX"
else
  export OS="Linux"
fi

export ARCH=`uname -m`

echo "Looking for Anaconda installation"
conda info > /dev/null
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
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-${OS}-${ARCH}.sh -O miniconda.sh;

  bash miniconda.sh -b -p $HOME/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  hash -r
  conda config --set always_yes yes --set changeps1 no
  conda update -q conda

  # Useful for debugging any issues with conda
  conda info -a
fi

conda env list | grep '^pyweed\s' > /dev/null
if (( $? )); then
  echo "Found a pyweed environment"
  ENV_ACTION="create"
else
  echo "No pyweed environment found"
  ENV_ACTION="update"
fi

echo "Working to $ENV_ACTION PyWEED environment"
wget https://raw.githubusercontent.com/iris-edu/pyweed/master/environment.yml -O environment.yml
conda env $ENV_ACTION
source activate pyweed

echo "Installing PyWEED"
pip install git+https://github.com/iris-edu/pyweed.git

if [[ $OS == 'MacOSX' ]]; then
  echo "Creating Mac app bundle"
  hash -r
  pyweed_install_osx
  echo "Copy $PWD/PyWEED.app to /Applications"
fi
