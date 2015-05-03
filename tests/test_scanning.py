import pytest

from moult import filesystem_scanner, utils
from moult.classes import PyModule


def test_data_integrity_check(data):
    data_dir = data.copy_data()
    py_script = data_dir.join('scripts/shell/python_script')

    assert data.sysexec(py_script)

    with pytest.raises(AssertionError):
        data.verify_data()

    data_dir = data.copy_data()
    bash_script = data_dir.join('scripts/shell/python_script')

    assert data.sysexec(bash_script)

    with pytest.raises(AssertionError):
        data.verify_data()


def test_scan_all(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()

    # Fake package that's imported from a script that shouldn't be scanned
    fakepkg = PyModule('fake_package', 'FAKE', '/a/fake/location')
    fakepkg.set_import_names(['fake_package', 'fake_package.spam'])
    installed.append(fakepkg)

    pkg = filesystem_scanner.scan(str(data_dir), installed)

    assert pkg.version == 'DIRECTORY'
    assert fakepkg not in pkg.dependencies, 'Fake package should not be a dependency'

    packages = ('moult', 'django', 'testpackage', 'boto', 'setuptools',
                'django-boto', 'django-allauth', 'django-mptt')

    for p in packages:
        dep = utils.find_package(p, installed, True)
        assert isinstance(dep, PyModule)
        assert dep in pkg.dependencies


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

    assert data.verify_data()


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

    data.verify_data()


def test_scan_module(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    module = data_dir.join('scripts/project/nested/scripts/testmodule')
    pkg = filesystem_scanner.scan(str(module), installed)

    assert pkg in installed
    assert pkg.name == 'testmodule'
    assert pkg.version == 'MODULE'

    assert utils.find_package('moult', installed, True) in pkg.dependencies
    assert utils.find_package('testpackage', installed, True) in pkg.dependencies


def test_scan_shell_scripts(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    shell_scripts = data_dir.join('scripts/shell')

    assert filesystem_scanner.scan(str(shell_scripts.join('bash_script')), installed) is None

    pkg = filesystem_scanner.scan(str(shell_scripts.join('python_script')), installed)
    assert pkg in installed
    assert pkg.version == 'SCRIPT'

    mpkg = utils.find_package('moult', installed, True)
    assert mpkg in pkg.dependencies

    data.verify_data()


def test_bad_tabs(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    bad_script = data_dir.join('scripts/loose/bad_tabs.py')

    mpkg1 = utils.find_package('moult', installed, True)
    mpkg2 = utils.find_package('testpackage', installed, True)

    pkg = filesystem_scanner.scan(str(bad_script), installed)
    assert pkg is not None
    assert mpkg1 in pkg.dependencies
    assert mpkg2 in pkg.dependencies

    data.verify_data()


def test_unicode_scan(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    unicode_script = data_dir.join('scripts/loose/unicode.py')

    mpkg = utils.find_package('moult', installed, True)
    pkg = filesystem_scanner.scan(unicode_script.strpath, installed)
    assert pkg is not None
    assert mpkg in pkg.dependencies


def test_unicode_import_scan(data):
    installed = data.copy_installed()
    data_dir = data.copy_data()
    unicode_script = data_dir.join('scripts/loose/unicode_import.py')

    mpkg = utils.find_package('moult', installed, True)
    pkg = filesystem_scanner.scan(unicode_script.strpath, installed)
    assert pkg is not None
    assert mpkg in pkg.dependencies
