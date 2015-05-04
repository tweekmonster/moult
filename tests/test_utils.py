import sys

import pytest

from moult import utils
from moult.classes import PyModule


python2_stdlib = (
    '__builtin__', '__future__', 'abc', 'aifc', 'anydbm', 'argparse', 'array',
    'ast', 'asynchat', 'asyncore', 'atexit', 'audioop', 'base64',
    'BaseHTTPServer', 'bdb', 'binascii', 'binhex', 'bisect', 'bsddb', 'bz2',
    'calendar', 'cgi', 'CGIHTTPServer', 'cgitb', 'chunk', 'cmath', 'cmd',
    'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall',
    'ConfigParser', 'contextlib', 'Cookie', 'cookielib', 'copy', 'copy_reg',
    'cPickle', 'cProfile', 'cStringIO', 'csv', 'ctypes', 'curses', 'datetime',
    'dbhash', 'decimal', 'difflib', 'dis', 'distutils', 'doctest',
    'DocXMLRPCServer', 'dumbdbm', 'dummy_thread', 'dummy_threading', 'email',
    'encodings', 'errno', 'exceptions', 'filecmp', 'fileinput',
    'fnmatch', 'formatter', 'fractions', 'ftplib', 'functools',
    'future_builtins', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'gzip',
    'hashlib', 'heapq', 'hmac', 'hotshot', 'htmlentitydefs', 'HTMLParser',
    'httplib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io',
    'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale',
    'logging', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math',
    'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'netrc',
    'nntplib', 'numbers', 'operator', 'os', 'parser', 'pdb', 'pickle',
    'pickletools', 'pkgutil', 'platform', 'plistlib', 'poplib', 'pprint',
    'profile', 'pstats', 'py_compile', 'pyclbr', 'pydoc', 'Queue', 'quopri',
    'random', 're', 'rlcompleter', 'robotparser', 'runpy', 'sched', 'select',
    'shelve', 'shlex', 'shutil', 'signal', 'SimpleHTTPServer',
    'SimpleXMLRPCServer', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket',
    'SocketServer', 'sqlite3', 'ssl', 'stat', 'string', 'StringIO',
    'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable',
    'sys', 'sysconfig', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile',
    'test', 'textwrap', 'thread', 'threading', 'time', 'timeit', 'Tix',
    'Tkinter', 'token', 'tokenize', 'trace', 'traceback', 'ttk', 'turtle',
    'types', 'unicodedata', 'unittest', 'urllib', 'urllib2', 'urlparse',
    'UserDict', 'UserList', 'UserString', 'uu', 'uuid', 'warnings', 'wave',
    'weakref', 'webbrowser', 'whichdb', 'wsgiref', 'xdrlib', 'xml',
    'xmlrpclib', 'zipfile', 'zipimport', 'zlib',
)


python3_stdlib = (
    '__future__', '_dummy_thread', '_thread', 'abc', 'aifc',
    'argparse', 'array', 'ast', 'asynchat', 'asyncore', 'atexit', 'audioop',
    'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2',
    'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
    'codeop', 'collections', 'colorsys', 'compileall', 'concurrent',
    'configparser', 'contextlib', 'copy', 'copyreg', 'cProfile', 'csv',
    'ctypes', 'curses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis',
    'distutils', 'doctest', 'dummy_threading', 'email', 'encodings',
    'errno', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions',
    'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob',
    'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr',
    'imp', 'importlib', 'inspect', 'io', 'itertools', 'json', 'keyword',
    'lib2to3', 'linecache', 'locale', 'logging', 'macpath', 'mailbox',
    'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder',
    'multiprocessing', 'netrc', 'nntplib', 'numbers', 'operator', 'os',
    'parser', 'pdb', 'pickle', 'pickletools', 'pkgutil', 'platform',
    'plistlib', 'poplib', 'pprint', 'profile', 'pstats', 'py_compile',
    'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'reprlib',
    'rlcompleter', 'runpy', 'sched', 'select', 'shelve', 'shlex', 'shutil',
    'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket',
    'socketserver', 'sqlite3', 'ssl', 'stat', 'string', 'struct',
    'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig',
    'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'test', 'textwrap',
    'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace',
    'traceback', 'turtle', 'types', 'unicodedata', 'unittest', 'urllib',
    'uu', 'uuid', 'warnings', 'wave', 'weakref', 'webbrowser', 'wsgiref',
    'xdrlib', 'xml', 'xmlrpc', 'zipfile', 'zipimport', 'zlib',
)


def test_installed_packages(data):
    installed = data.copy_installed()
    assert len(installed)

    for pkg in installed:
        assert isinstance(pkg, PyModule), 'Item in installed packages is not a PyModule instance'
        assert len(pkg.import_names), 'Installed package has no import path names'
        pkg2 = PyModule(pkg.name, pkg.version, pkg.location, pkg.missing)
        assert hash(pkg) == hash(pkg2), '__hash__ failure in PyModule'


@pytest.mark.skipif(sys.version_info[:2] > (2, 7), reason='Requires Python 2.7')
def test_python2_stdlib():
    print(sys.version_info)
    for lib in python2_stdlib:
        assert utils.is_stdlib(lib)


@pytest.mark.skipif(sys.version_info[:2] < (3, 2), reason='Requires Python 3.2+')
def test_python3_stdlib():
    print(sys.version_info)
    for lib in python3_stdlib:
        assert utils.is_stdlib(lib)


def test_not_stdlib():
    assert not utils.is_stdlib('moult')
    assert not utils.is_stdlib('moult.utils')
    assert not utils.is_stdlib('spam')
    assert not utils.is_stdlib('spam.eggs.bacon')
    assert not utils.is_stdlib('somefile.py')
    assert not utils.is_stdlib('/some/path')


def test_is_import_str():
    assert utils.is_import_str('spam.eggs.cheese')
    assert not utils.is_import_str('spam')
    assert not utils.is_import_str('/path/to/someplace.txt')


def test_resolve_import():
    from_module = 'spam.eggs.cheese'

    assert utils.resolve_import('.bacon', from_module) == 'spam.eggs.bacon'
    assert utils.resolve_import('..bacon', from_module) == 'spam.bacon'
    assert utils.resolve_import('...bacon', from_module) == 'bacon'
    assert utils.resolve_import('....bacon', from_module) == 'bacon'


def test_find_package(data):
    installed = data.copy_installed()
    pkg = utils.find_package('moult', installed, package=True)
    assert pkg and pkg.name == 'moult'

    pkg = utils.find_package('moult.utils', installed, package=True)
    assert pkg is None

    pkg = utils.find_package('does.not.exist', installed)
    assert pkg is None

    pkg = utils.find_package('moult', installed)
    assert pkg and pkg.name == 'moult'

    # Searching for module imports should only match their top level
    # import names
    pkg = utils.find_package('moult.utils.does.not.exist', installed)
    assert pkg is None

    pkg = utils.find_package('pkg_resources', installed)
    assert pkg and pkg.name == 'setuptools'


def test_find_file(data):
    data_dir = data.copy_data()
    filename = str(data_dir.join('scripts/project/nested/scripts/testmodule/utils/spam.py'))
    root = str(data_dir.join('scripts/project/nested/scripts/testmodule'))
    import_file = utils.file_containing_import('utils.spam.SomeClass', root)
    assert import_file == filename


def test_file_types(data):
    datadir = data.copy_data()
    bash_script = str(datadir.join('scripts/shell/bash_script'))
    py_script = str(datadir.join('scripts/shell/python_script'))

    assert utils.is_script(bash_script)
    assert not utils.is_python_script(bash_script)
    assert utils.is_script(py_script)
    assert utils.is_python_script(py_script)
