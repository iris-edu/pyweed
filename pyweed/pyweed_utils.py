"""
Pyweed utility functions.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import os
import logging

LOGGER = logging.getLogger(__name__)


def manageCache(downloadDir, cacheSize):
    """
    Maintain a cache directory at a certain size (MB) by removing the oldest files.
    """

    try:
        # Compile statistics on all files in the output directory and subdirectories
        stats = []
        totalSize = 0
        for root, dirs, files in os.walk(downloadDir):
            for file in files:
                path = os.path.join(root,file)
                statList = os.stat(path)
                # path, size, atime
                newStatList = [path, statList.st_size, statList.st_atime]
                totalSize = totalSize + statList.st_size
                # don't want hidden files like .htaccess so don't add stuff that starts with .
                if not file.startswith('.'):
                    stats.append(newStatList)

        # Sort file stats by last access time
        stats = sorted(stats, key=lambda file: file[2])

        # Delete old files until we get under cacheSize (configured in megabytes)
        deletionCount = 0
        while totalSize > cacheSize * 1000000:
            # front of stats list is the file with the smallest (=oldest) access time
            lastAccessedFile = stats[0]
            # index 1 is where size is
            totalSize = totalSize - lastAccessedFile[1]
            # index 0 is where path is
            os.remove(lastAccessedFile[0])
            # remove the file from the stats list
            stats.pop(0)
            deletionCount = deletionCount + 1

        LOGGER.debug('Removed %d files to keep %s below %.0f megabytes' % (deletionCount, downloadDir, cacheSize))


    except Exception, e:
        LOGGER.error(str(e))


