import os
import re
import sys

from .classes import PyModule
from .pip_importer import *
from .compat import str_

_stdlib = set()
_import_paths = []


__all__ = ('dist_is_local', 'dist_in_usersite', 'get_installed_distributions',
           'running_under_virtualenv', 'ignore_packages',
           'search_packages_info', 'find_package')


def load_stdlib():
    '''Scans sys.path for standard library modules.
    '''
    if _stdlib:
        return _stdlib

    prefixes = tuple({os.path.abspath(p) for p in (
        sys.prefix,
        getattr(sys, 'real_prefix', sys.prefix),
        getattr(sys, 'base_prefix', sys.prefix),
    )})

    for sp in sys.path:
        if not sp:
            continue
        _import_paths.append(os.path.abspath(sp))

    stdpaths = tuple({p for p in _import_paths
                      if p.startswith(prefixes) and 'site-packages' not in p})

    _stdlib.update(sys.builtin_module_names)

    for stdpath in stdpaths:
        if not os.path.isdir(stdpath):
            continue

        for item in os.listdir(stdpath):
            if item.startswith('.') or item == 'site-packages':
                continue

            p = os.path.join(stdpath, item)
            if not os.path.isdir(p) and not item.endswith(('.py', '.so')):
                continue

            _stdlib.add(item.split('.', 1)[0])

    return _stdlib


load_stdlib()


def is_stdlib(module):
    return module.split('.', 1)[0] in load_stdlib()


def is_import_str(text):
    text = str_(text)
    return re.match(r'^[\w\.]+$', text) and re.match(r'\w+\.\w+', text)


def import_path_from_file(filename, as_list=False):
    '''Returns a tuple of the import path and root module directory for the
    supplied file.
    '''
    module_path = []
    basename = os.path.splitext(os.path.basename(filename))[0]
    if basename != '__init__':
        module_path.append(basename)

    dirname = os.path.dirname(filename)
    while os.path.isfile(os.path.join(dirname, '__init__.py')):
        dirname, tail = os.path.split(dirname)
        module_path.insert(0, tail)

    if as_list:
        return module_path, dirname
    return '.'.join(module_path), dirname


def file_containing_import(import_path, import_root):
    '''Finds the file that might contain the import_path.
    '''
    if not _import_paths:
        load_stdlib()

    if os.path.isfile(import_root):
        import_root = os.path.dirname(import_root)

    search_paths = [import_root] + _import_paths
    module_parts = import_path.split('.')
    for i in range(len(module_parts), 0, -1):
        module_path = os.path.join(*module_parts[:i])
        for sp in search_paths:
            p = os.path.join(sp, module_path)
            if os.path.isdir(p):
                return os.path.join(p, '__init__.py')
            elif os.path.isfile(p + '.py'):
                return p + '.py'
    return None


def resolve_import(import_path, from_module):
    '''Resolves relative imports from a module.
    '''
    if not import_path or not import_path.startswith('.'):
        return import_path

    from_module = from_module.split('.')
    dots = 0
    for c in import_path:
        if c == '.':
            dots += 1
        else:
            break

    if dots:
        from_module = from_module[:-dots]
        import_path = import_path[dots:]

    if import_path:
        from_module.append(import_path)

    return '.'.join(from_module)


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
            return re.match(r'.*python', str_(fp.readline()))
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
