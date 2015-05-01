import os
import re

from .classes import PyModule
from .pip_importer import *
from .version import PY3


__all__ = ('dist_is_local', 'dist_in_usersite', 'get_installed_distributions',
           'running_under_virtualenv', 'ignore_packages', 'search_packages_info',

           'find_package', 'scan_file', 'scan_directory')

if not PY3:
    str = unicode


def find_package(name, installed, package=False):
    '''Finds a package in the installed list.

    If `package` is true, match package names, otherwise, match import paths.
    '''
    if package:
        name = name.lower()
        tests = (
            lambda x: x.user and name == x.name.lower(),
            lambda x: x.local and name == x.name.lower(),
            lambda x: name == x.name.lower(),
        )
    else:
        tests = (
            lambda x: x.user and name in x.import_names,
            lambda x: x.local and name in x.import_names,
            lambda x: name in x.import_names,
        )

    for t in tests:
        try:
            found = list(filter(t, installed))
            if found and not found[0].is_scan:
                return found[0]
        except StopIteration:
            pass
    return None


def is_script(filename):
    '''Checks if a file has a hashbang.
    '''
    if not os.path.isfile(filename):
        return False

    try:
        with open(filename, 'rb') as fp:
            return fp.read(2) == b'#!'
    except IOError:
        pass

    return False


def is_python_script(filename):
    '''Checks a file to see if it's a python script of some sort.
    '''
    if filename.lower().endswith('.py'):
        return True

    if not os.path.isfile(filename):
        return False

    try:
        with open(filename, 'rb') as fp:
            if fp.read(2) != b'#!':
                return False
            return re.match(r'.*python', str(fp.readline()))
    except IOError:
        pass

    return False


def iter_dist_files(dist):
    if dist.has_metadata('RECORD'):
        for line in dist.get_metadata_lines('RECORD'):
            line = line.split(',')[0]
            if line.endswith('.pyc'):
                continue
            yield os.path.normpath(os.path.join(dist.location, line))
    elif dist.has_metadata('installed-files.txt'):
        for line in dist.get_metadata_lines('installed-files.txt'):
            if line.endswith('.pyc'):
                continue
            yield os.path.normpath(os.path.join(dist.location,
                                                dist.egg_info, line))


def installed_packages(local=False):
    installed = []

    for dist in get_installed_distributions(local_only=local):
        pym = PyModule(dist.project_name, dist.version, dist.location)
        if dist.has_metadata('top_level.txt'):
            pym.set_import_names(list(dist.get_metadata_lines('top_level.txt')))

        pym.local = dist_is_local(dist)
        pym.user = dist_in_usersite(dist)
        pym._dependencies = [dep.project_name for dep in dist.requires()]

        for filename in iter_dist_files(dist):
            if not filename.startswith(dist.location):
                if is_script(filename):
                    pym.installed_scripts.append(filename)
                else:
                    pym.installed_files.append(filename)

        if pym.installed_scripts or pym.name in ignore_packages:
            pym.hidden = True

        installed.append(pym)

    for pym in installed[:]:
        for dep in pym._dependencies:
            if dep == 'argparse':
                # Since I'm only testing with Python 2.7, skip any requirements
                # for argparse.
                continue
            pymc = find_package(dep, installed, True)
            if not pymc:
                pymc = PyModule(dep, 'MISSING', missing=True)
                installed.append(pymc)
            pymc.add_dependant(pym)
            pym.add_dependency(pymc)

    return installed
