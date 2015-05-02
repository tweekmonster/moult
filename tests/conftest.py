import os
import copy
import pytest

from moult.utils import installed_packages

from py._path.local import LocalPath


class ScriptData(object):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir
        self.installed_packages = None

    def copy_data(self):
        datadir = self.tmpdir.mkdir('data')
        data = LocalPath(os.path.dirname(__file__)).join('data')
        data.copy(datadir)
        return datadir

    def copy_installed(self):
        if not self.installed_packages:
            self.installed_packages = installed_packages()
        return copy.deepcopy(self.installed_packages)


@pytest.fixture
def data(tmpdir):
    return ScriptData(tmpdir)
