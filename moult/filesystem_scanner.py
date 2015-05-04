import os
import re

from .classes import PyModule
from .ast_scanner import ast_scan_file
from .frameworks import django
from . import utils, log


max_directory_depth = 20
max_file_size = 1024 * 1204

# Common ignorable directories
_dir_ignore = re.compile(r'(\.(git|hg|svn|tox)|CVS|__pycache__)\b')

# Files to not even bother with scanning
_ext_ignore = re.compile(r'\.(pyc|html|js|css|zip|tar(\.gz)?|txt|swp|~|bak|db)$', re.I)


def _scan_file(filename, sentinel, source_type='import'):
    '''Generator that performs the actual scanning of files.

    Yeilds a tuple containing import type, import path, and an extra file
    that should be scanned. Extra file scans should be the file or directory
    that relates to the import name.
    '''
    filename = os.path.abspath(filename)
    real_filename = os.path.realpath(filename)

    if os.path.getsize(filename) <= max_file_size:
        if real_filename not in sentinel and os.path.isfile(filename):
            sentinel.add(real_filename)

            basename = os.path.basename(filename)
            scope, imports = ast_scan_file(filename)

            if scope is not None and imports is not None:
                for imp in imports:
                    yield (source_type, imp.module, None)

                if 'INSTALLED_APPS' in scope and basename == 'settings.py':
                    log.info('Found Django settings: %s', filename)
                    for item in django.handle_django_settings(filename):
                        yield item
            else:
                log.warn('Could not scan imports from: %s', filename)
    else:
        log.warn('File size too large: %s', filename)


def _scan_directory(directory, sentinel, depth=0):
    '''Basically os.listdir with some filtering.
    '''
    directory = os.path.abspath(directory)
    real_directory = os.path.realpath(directory)

    if depth < max_directory_depth and real_directory not in sentinel \
            and os.path.isdir(directory):
        sentinel.add(real_directory)

        for item in os.listdir(directory):
            if item in ('.', '..'):
                # I'm not sure if this is even needed any more.
                continue

            p = os.path.abspath(os.path.join(directory, item))
            if (os.path.isdir(p) and _dir_ignore.search(p)) \
                    or (os.path.isfile(p) and _ext_ignore.search(p)):
                continue

            yield p


def scan_file(pym, filename, sentinel, installed):
    '''Entry point scan that creates a PyModule instance if needed.
    '''
    if not utils.is_python_script(filename):
        return

    if not pym:
        # This is for finding a previously created instance, not finding an
        # installed module with the same name. Might need to base the name
        # on the actual paths to reduce ambiguity in the printed scan results.
        module = os.path.basename(filename)
        pym = utils.find_package(module, installed)
        if not pym:
            pym = PyModule(module, 'SCRIPT', os.path.abspath(filename))
            installed.insert(0, pym)
        else:
            pym.is_scan = True

    for imp_type, import_path, extra_file_scan in _scan_file(filename, sentinel):
        dep = utils.find_package(import_path, installed)
        if dep:
            dep.add_dependant(pym)
            pym.add_dependency(dep)

            if imp_type != 'import':
                pym.add_framework(imp_type)

        if extra_file_scan:
            # extra_file_scan should be a directory or file containing the
            # import name
            scan_filename = utils.file_containing_import(import_path, extra_file_scan)
            log.info('Related scan: %s - %s', import_path, scan_filename)
            if scan_filename.endswith('__init__.py'):
                scan_directory(pym, os.path.dirname(scan_filename), sentinel, installed)
            else:
                scan_file(pym, scan_filename, sentinel, installed)

    return pym


def scan_directory(pym, directory, sentinel, installed, depth=0):
    '''Entry point scan that creates a PyModule instance if needed.
    '''
    if not pym:
        d = os.path.abspath(directory)
        basename = os.path.basename(d)
        pym = utils.find_package(basename, installed)
        if not pym:
            version = 'DIRECTORY'
            if os.path.isfile(os.path.join(d, '__init__.py')):
                version = 'MODULE'
            pym = PyModule(basename, version, d)
            installed.insert(0, pym)
        else:
            pym.is_scan = True

    # Keep track of how many file scans resulted in nothing
    bad_scans = 0

    for item in _scan_directory(directory, sentinel, depth):
        if os.path.isfile(item):
            if bad_scans > 100:
                # Keep in mind this counter resets if it a good scan happens
                # in *this* directory. If you have a module with more than 100
                # files in a single directory, you should probably refactor it.
                log.debug('Stopping scan of directory since it looks like a data dump: %s', directory)
                break

            if not scan_file(pym, item, sentinel, installed):
                bad_scans += 1
            else:
                bad_scans = 0
        elif os.path.isdir(item):
            scan_directory(pym, item, sentinel, installed, depth + 1)

    return pym


def scan(filename, installed, sentinel=None):
    if not sentinel:
        sentinel = set()

    if os.path.isfile(filename):
        return scan_file(None, filename, sentinel, installed)
    elif os.path.isdir(filename):
        return scan_directory(None, filename, sentinel, installed)
    else:
        log.error('Could not scan: %s', filename)
