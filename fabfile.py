from fabric.api import task, hosts, local
from glob import glob

@task
@hosts('localhost')
def build_uic():
    """Rebuild the Qt Creator UI files"""
    for ui_file in glob('pyweed/gui/uic/*.ui'):
        py_file = ui_file.rsplit('.', 1)[0] + '.py'
        local("pyuic4 %s -o %s" % (ui_file, py_file))

