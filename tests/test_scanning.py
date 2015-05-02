from moult import filesystem_scanner, utils


def test_nested_directory(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    nested = str(data_dir.join('scripts/project/nested'))
    pkg = filesystem_scanner.scan(nested, installed)
    assert pkg in installed
    assert pkg.location == nested
    assert pkg.name == 'nested'
    assert pkg.version == 'DIRECTORY'
    assert not pkg.frameworks

    packages = ('moult', 'setuptools', 'testpackage')
    for p in packages:
        dep = utils.find_package(p, installed, True)
        assert dep in pkg.dependencies


def test_scan_nested_file(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    filename = str(data_dir.join('scripts/project/nested/scripts/testmodule/utils/spam.py'))

    pkg = filesystem_scanner.scan_file(None, filename, set(), installed)
    assert pkg in installed
    assert pkg.location == filename
    assert pkg.name == 'spam.py'
    assert pkg.version == 'SCRIPT'
    assert not pkg.frameworks


def test_scan_django(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    django_project = str(data_dir.join('scripts/project/django_project'))
    pkg = filesystem_scanner.scan(django_project, installed)
    assert pkg in installed
    assert pkg.location == django_project
    assert pkg.name == 'django_project'
    assert pkg.version == 'DIRECTORY'
    assert 'django' in pkg.frameworks
    packages = ('django', 'testpackage', 'django-allauth', 'django-boto', 'django-mptt', 'boto')
    for p in packages:
        dep = utils.find_package(p, installed, True)
        assert dep in pkg.dependencies
