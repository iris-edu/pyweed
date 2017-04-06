#-----------------------------------------------------------------------------
# Based on examples at https://github.com/pyinstaller/pyinstaller/blob/develop/PyInstaller/hooks/
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, exec_statement, copy_metadata,\
    collect_submodules, get_package_paths
import os.path

(_, obspy_root) = get_package_paths('obspy')

binaries = collect_dynamic_libs('obspy')
datas = [
    # Dummy path, this needs to exist because ObsPy loads a library relative to this path
    (os.path.join(obspy_root, "*.txt"), os.path.join('obspy', 'core', 'util')),
    # Data
    (os.path.join(obspy_root, "imaging", "data"), os.path.join('obspy', 'imaging', 'data')),
    (os.path.join(obspy_root, "taup", "data"), os.path.join('obspy', 'taup', 'data')),
    (os.path.join(obspy_root, "geodetics", "data"), os.path.join('obspy', 'geodetics', 'data')),
]
# Plugins are defined in the metadata (.egg-info) directory, but if we grab the whole thing it causes
# other errors, so include only entry_points.txt
metadata = copy_metadata('obspy')
metadata = [(os.path.join(metadata[0][0], 'entry_points.txt'), metadata[0][1])]
datas += metadata

# Include the actual plugin packages
hiddenimports = collect_submodules('obspy.io')
