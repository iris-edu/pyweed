#! env python

import sys
from pyweed import __version__, __app_name__, __pkg_path___
import os
from shutil import copy2
import pkg_resources


def build_mac_launcher():
    """
    Build an .app bundle on Mac
    """
    base_path = "%s.app" % __app_name__

    os.makedirs(os.path.join(base_path, "Contents", "MacOS"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "Contents", "Resources"), exist_ok=True)

    bundle_identifier = "edu.iris.%s" % __app_name__
    app_version_string = "%s %s" % (__app_name__, __version__)

    with open(os.path.join(base_path, "Contents", "Info.plist"), "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>CFBundleDevelopmentRegion</key>
            <string>English</string>
            <key>CFBundleExecutable</key>
            <string>%s</string>
            <key>CFBundleGetInfoString</key>
            <string>%s</string>
            <key>CFBundleIconFile</key>
            <string>app.icns</string>
            <key>CFBundleIdentifier</key>
            <string>%s</string>
            <key>CFBundleInfoDictionaryVersion</key>
            <string>6.0</string>
            <key>CFBundleName</key>
            <string>%s</string>
            <key>CFBundlePackageType</key>
            <string>APPL</string>
            <key>CFBundleShortVersionString</key>
            <string>%s</string>
            <key>CFBundleSignature</key>
            <string>????</string>
            <key>CFBundleVersion</key>
            <string>%s</string>
            <key>NSAppleScriptEnabled</key>
            <string>YES</string>
            <key>NSMainNibFile</key>
            <string>MainMenu</string>
            <key>NSPrincipalClass</key>
            <string>NSApplication</string>
        </dict>
        </plist>
        """ % (__app_name__, app_version_string, bundle_identifier, __app_name__, app_version_string, __version__))

    with open(os.path.join(base_path, "Contents", "PkgInfo"), "w") as f:
        f.write("APPL????")

    icons_stream = pkg_resources.resource_stream('pyweed', 'app.icns')
    with open(os.path.join(base_path, "Contents", "Resources", "app.icns"), "wb") as f:
        f.write(icons_stream.read())

    # This is the executable script packaged up by setup.py
    conda_bin_path = os.path.dirname(sys.executable)
    bin_src = os.path.join(conda_bin_path, 'pyweed')
    # We will copy it into the app bundle
    bin_dest = os.path.join(base_path, "Contents", "MacOS", __app_name__)
    copy2(bin_src, bin_dest)


def build_windows_launcher():
    """
    Build a batch file launcher for Windows
    """
    bat_file = '%s.bat' % __app_name__
    with open(bat_file, "w") as f:
        f.write("""%s -m pyweed.pyweed_launcher""" % sys.executable)


def build():
    if sys.platform.startswith('win'):
        build_windows_launcher()
    elif sys.platform.startswith('darwin'):
        build_mac_launcher()


if __name__ == '__main__':
    build()
