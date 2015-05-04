from __future__ import absolute_import, unicode_literals

import re
import os
import sys
import time

from .. import utils, log


_excluded_settings = (
    'ALLOWED_HOSTS',
)

_filescan_modules = (
    'django.db.backends',
    'django.core.cache.backends',
)


def scan_django_settings(values, imports):
    '''Recursively scans Django settings for values that appear to be
    imported modules.
    '''
    if isinstance(values, (str, bytes)):
        if utils.is_import_str(values):
            imports.add(values)
    elif isinstance(values, dict):
        for k, v in values.items():
            scan_django_settings(k, imports)
            scan_django_settings(v, imports)
    elif hasattr(values, '__file__') and getattr(values, '__file__'):
        imp, _ = utils.import_path_from_file(getattr(values, '__file__'))
        imports.add(imp)
    elif hasattr(values, '__iter__'):
        for item in values:
            scan_django_settings(item, imports)


def handle_django_settings(filename):
    '''Attempts to load a Django project and get package dependencies from
    settings.

    Tested using Django 1.4 and 1.8. Not sure if some nuances are missed in
    the other versions.
    '''
    old_sys_path = sys.path[:]
    dirpath = os.path.dirname(filename)
    project = os.path.basename(dirpath)
    cwd = os.getcwd()
    project_path = os.path.normpath(os.path.join(dirpath, '..'))
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    os.chdir(project_path)

    project_settings = '{}.settings'.format(project)
    os.environ['DJANGO_SETTINGS_MODULE'] = project_settings

    try:
        import django
        # Sanity
        django.setup = lambda: False
    except ImportError:
        log.error('Found Django settings, but Django is not installed.')
        return

    log.warn('Loading Django Settings (Using {}): {}'
                    .format(django.get_version(), filename))

    from django.conf import LazySettings

    installed_apps = set()
    settings_imports = set()

    try:
        settings = LazySettings()
        settings._setup()
        for k, v in vars(settings._wrapped).items():
            if k not in _excluded_settings and re.match(r'^[A-Z_]+$', k):
                # log.debug('Scanning Django setting: %s', k)
                scan_django_settings(v, settings_imports)

        # Manually scan INSTALLED_APPS since the broad scan won't include
        # strings without a period in it .
        for app in getattr(settings, 'INSTALLED_APPS', []):
            if hasattr(app, '__file__') and getattr(app, '__file__'):
                imp, _ = utils.import_path_from_file(getattr(app, '__file__'))
                installed_apps.add(imp)
            else:
                installed_apps.add(app)
    except Exception as e:
        log.error('Could not load Django settings: %s', e)
        log.debug('', exc_info=True)
        return

    if not installed_apps or not settings_imports:
        log.error('Got empty settings values from Django settings.')

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
                    installed_apps.add(app.name)
            except AppRegistryNotReady:
                if time.time() - start > 10:
                    raise Exception('Bail out of waiting for Django')
                log.debug('Waiting for apps to load...')
                continue
            break
    except Exception as e:
        log.debug('Could not use AppConfig: {}'.format(e))

    # Restore before sub scans can occur
    sys.path[:] = old_sys_path
    os.chdir(cwd)

    for item in settings_imports:
        need_scan = item.startswith(_filescan_modules)
        yield ('django', item, project_path if need_scan else None)

    for app in installed_apps:
        need_scan = app.startswith(project)
        yield ('django', app, project_path if need_scan else None)
