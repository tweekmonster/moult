import os
import copy
import pytest
import logging


from moult import log
from moult.utils import installed_packages

from py._path.local import LocalPath


log.set_level(logging.DEBUG)


class ScriptData(object):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir
        self.tmpdata = None
        self.pristine_data = LocalPath(os.path.dirname(__file__)).join('data')
        self.installed_packages = None

    def copy_data(self):
        if self.tmpdata and self.tmpdata.exists():
            self.tmpdata.remove(ignore_errors=True)
        self.tmpdata = self.tmpdir.mkdir('data')
        self.pristine_data.copy(self.tmpdata, mode=True)

        # Can't add .git directories to the index
        git_no_scan = self.pristine_data.join('scripts/project/.hg')
        hg_no_scan = self.tmpdata.join('scripts/project/.git')
        git_no_scan.copy(hg_no_scan)

        return self.tmpdata

    def sysexec(self, script):
        print('Executing Script: %s' % script)
        return script.sysexec(cwd=str(script.dirpath()))

    def verify_data(self):
        if not self.tmpdata:
            return False

        for prissy in self.pristine_data.visit():
            assert prissy.ext != '.pyc', \
                'Pristine has Python bytecode indicating execution from pristine directory!'

            rel = prissy.relto(self.pristine_data)
            tmp = self.tmpdata.join(rel)

            if prissy.check(dir=True):
                assert tmp.check(dir=True), 'Data integirty test failed: %s' % rel
            elif prissy.check(file=True):
                assert tmp.check(file=True), 'Data integirty test failed: %s' % rel
                assert prissy.computehash() == tmp.computehash(), 'Hash mismatch: %s' % rel

        for tmp in self.tmpdata.visit():
            if '.git' in tmp.strpath or '__pycache__' in tmp.strpath or tmp.ext == '.pyc':
                continue

            rel = tmp.relto(self.tmpdata)
            prissy = self.pristine_data.join(rel)

            if tmp.check(dir=True):
                assert prissy.check(dir=True), 'Directory created in tmpdir: %s' % rel
            elif tmp.check(file=True):
                assert prissy.check(file=True), 'File created in tmpdir: %s' % rel

        return True

    def copy_installed(self):
        if not self.installed_packages:
            self.installed_packages = installed_packages()
        return copy.deepcopy(self.installed_packages)


@pytest.fixture
def data(tmpdir):
    return ScriptData(tmpdir)
