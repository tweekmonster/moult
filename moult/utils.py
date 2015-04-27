import os
import re
import sys
import time

from .classes import PyModule
from .pip_importer import *
from .version import PY3
from . import printer


__all__ = ('dist_is_local', 'dist_in_usersite', 'get_installed_distributions',
           'running_under_virtualenv', 'ignore_packages', 'search_packages_info',

           'find_package', 'scan_file', 'scan_directory')

if not PY3:
    str = unicode

# Common ignorable directories
_dir_ignore = re.compile(r'(\.(git|hg|svn)|CVS|__pycache__)\b')

# Files to not even bother with scanning
_ext_ignore = re.compile(r'\.(pyc|html|js|css|zip|tar(\.gz)?|txt|swp|~|bak|db)$', re.I)
_scan_cache = set()


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


def handle_django_settings(filename):
    '''Attempts to load a Django project and get package dependencies from
    settings.

    Tested using Django 1.4 and 1.8. Not sure if some nuances are missed in
    the other versions.
    '''

    dirpath = os.path.dirname(filename)
    project = os.path.basename(dirpath)
    cwd = os.getcwd()
    project_path = os.path.normpath(os.path.join(dirpath, '..'))
    remove_path = project_path not in sys.path
    if remove_path:
        sys.path.insert(0, project_path)
    os.chdir(project_path)

    os.environ['DJANGO_SETTINGS_MODULE'] = '{}.settings'.format(project)

    try:
        import django
        # Sanity
        django.setup = lambda: False
    except ImportError:
        printer.error('Found Django settings, but Django is not installed.')
        return

    printer.error('Loading Django Settings (Using {}): {}'
                    .format(django.get_version(), filename))

    from django.conf import LazySettings

    installed_apps = None
    db_settings = None
    cache_settings = None

    try:
        settings = LazySettings()
        installed_apps = getattr(settings, 'INSTALLED_APPS', None)
        db_settings = getattr(settings, 'DATABASES', None)
        cache_settings = getattr(settings, 'CACHES', None)
    except Exception as e:
        printer.error(u'Could not load Django settings: {}'.format(e))
        return

    if not installed_apps or not db_settings:
        printer.error(u'Could not load INSTALLED_APPS or DATABASES.')

    # Find typical Django modules that rely on packages that the user chooses
    # to install.
    django_base = os.path.normpath(os.path.join(os.path.dirname(django.__file__), '..'))
    django_modules = set()
    if db_settings:
        for backend, db_conf in db_settings.items():
            engine = db_conf.get('ENGINE')
            if not engine:
                continue
            if hasattr(engine, '__file__'):
                django_modules.add(engine.__file__)
            else:
                p = os.path.join(django_base, *engine.split('.'))
                django_modules.add(os.path.join(p, 'base.py'))

    if cache_settings:
        for backend, cache_conf in cache_settings.items():
            engine = cache_conf.get('BACKEND')
            if hasattr(engine, '__file__'):
                django_modules.add(engine.__file__)
            else:
                p = os.path.join(django_base, *engine.split('.')[:-1])
                django_modules.add(p + '.py')

    if django_modules:
        for mod in django_modules:
            if os.path.exists(mod):
                for item in _scan_file(mod, 'django'):
                    yield item

    django_installed_apps = []

    try:
        from django.apps.registry import apps, Apps, AppRegistryNotReady
        # Django doesn't like it when the initial instance of `apps` is reused,
        # but it has to be populated before other instances can be created.
        if not apps.apps_ready:
            apps.populate(installed_apps)
        else:
            apps = Apps(installed_apps)

        start = time.time()
        while True:
            try:
                for app in apps.get_app_configs():
                    django_installed_apps.append(app.name)
            except AppRegistryNotReady:
                if time.time() - start > 10:
                    raise Exception('Bail out of waiting for Django')
                printer.debug('Waiting for apps to load...')
                continue
            break
    except Exception as e:
        django_installed_apps = list(installed_apps)
        printer.debug('Could not use AppConfig: {}'.format(e))

    for app in django_installed_apps:
        import_parts = app.split('.')
        # Start with the longest import path and work down
        for i in range(len(import_parts), 0, -1):
            yield ('django', '.'.join(import_parts[:i]))

    os.chdir(cwd)
    if remove_path:
        sys.path.remove(project_path)


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


def _scan_file(filename, source_type='import'):
    if filename not in _scan_cache and os.path.isfile(filename):
        basename = os.path.basename(filename)

        try:
            with open(filename, 'r') as fp:
                for line in fp.readlines():
                    m = re.search(r'^\s*(from|import)\s*(\w+)', line)
                    if m:
                        yield (source_type, m.group(2))

                    if source_type != 'import':
                        # Not sure if this is really needed, but seems alright
                        # to avoid recursive scanning of framework files
                        continue

                    if basename == 'settings.py' and \
                            re.search(r'INSTALLED_APPS\s*=', line):
                        for item in handle_django_settings(filename):
                            yield item
        except IOError as e:
            output.error('Could not read: {} - {}'.format(filename, e))
        finally:
            _scan_cache.add(filename)


def scan_file(pym, filename, installed):
    if not is_python_script(filename):
        return

    if not pym:
        # This is for finding a previously created instance, not finding an
        # installed module with the same name. Might need to base the name
        # on the actual paths to reduce ambiguity in the printed scan results.
        module = os.path.basename(filename)
        pym = find_package(module, installed)
        if not pym:
            pym = PyModule(module, 'SCRIPT', filename)
            installed.insert(0, pym)

    for imp_type, imported in _scan_file(filename):
        dep = find_package(imported, installed)
        if dep:
            dep.add_dependant(pym)
            pym.add_dependency(dep)

            if imp_type != 'import':
                pym.add_framework(imp_type)


def scan_directory(directory, installed, depth=0, pym=None, scanned=None):
    if not scanned:
        scanned = []

    directory = os.path.realpath(directory)

    if directory in scanned:
        return
    scanned.append(directory)

    if _dir_ignore.search(directory):
        return

    for item in os.listdir(directory):
        if item in ('.', '..'):
            continue

        p = os.path.normpath(os.path.join(directory, item))
        if os.path.isdir(p) and depth < 20:
            pym_sub = pym
            if not pym_sub:
                pym_sub = find_package(item, installed)
                if not pym_sub:
                    version = 'DIRECTORY'
                    if os.path.exists(os.path.join(p, '__init__.py')):
                        version = 'MODULE'
                    pym_sub = PyModule(item, version, p)
                    installed.insert(0, pym_sub)
            scan_directory(p, installed, depth=depth + 1, pym=pym_sub,
                            scanned=scanned)
            continue

        if not _ext_ignore.search(item):
            scan_file(pym, p, installed)


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
