#! env python

import sys
from pyweed import __version__, __app_name__, __pkg_path___
import os
from shutil import copy2
import pkg_resources


def main():
    base_path = "%s.app" % __app_name__

    os.makedirs("%s/Contents/MacOS" % base_path, exist_ok=True)
    os.makedirs("%s/Contents/Resources" % base_path, exist_ok=True)

    bundle_identifier = "edu.iris.%s" % __app_name__
    app_version_string = "%s %s" % (__app_name__, __version__)

    with open("%s/Contents/Info.plist" % base_path, "w") as f:
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

    with open("%s/Contents/PkgInfo" % base_path, "w") as f:
        f.write("APPL????")

    icons_stream = pkg_resources.resource_stream('pyweed', 'app.icns')
    with open("%s/Contents/Resources/app.icns" % base_path, "wb") as f:
        f.write(icons_stream.read())

    # This is the executable script packaged up by setup.py
    conda_bin_path = os.path.dirname(sys.executable)
    bin_src = os.path.join(conda_bin_path, 'pyweed')
    # We will copy it into the app bundle
    bin_dest = "%s/Contents/MacOS/%s" % (base_path, __app_name__)
    copy2(bin_src, bin_dest)


if __name__ == '__main__':
    main()
