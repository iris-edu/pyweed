if [[ `uname -s` == "Darwin" ]]; then
  export OS="MacOSX"
else
  export OS="Linux"
fi
echo "Identified OS as $OS"

# Run in /tmp/
cd /tmp/

export ARCH=`uname -m`

echo "Looking for Anaconda installation"
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

  bash miniconda.sh -b -p $HOME/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  hash -r
  conda config --set always_yes yes --set changeps1 no
  conda update -q conda

  # Useful for debugging any issues with conda
  conda info -a
else
  echo "Found Anaconda at" `conda info --root`
fi

conda env list | grep '^pyweed\s' > /dev/null
if (( $? )); then
  echo "No pyweed environment found"
  ENV_ACTION="create"
else
  echo "Found a pyweed environment"
  ENV_ACTION="update"
fi

echo "Working to $ENV_ACTION PyWEED environment"
curl -Ss -o environment.yml https://raw.githubusercontent.com/iris-edu/pyweed/master/environment.yml
conda env $ENV_ACTION
source activate pyweed

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
    mv $PWD/PyWEED.app /Applications/
    echo "Installed to /Applications/PyWEED.app"
  fi
fi

echo "Done!"
