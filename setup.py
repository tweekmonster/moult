import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

try:
    from pypandoc import convert

    def readme_file(readme):
        return convert(readme, 'rst')
except ImportError:
    def readme_file(readme):
        with open(readme, 'r') as fp:
            return fp.read()

moult = __import__('moult')

description = moult.__doc__.strip()


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex

        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='moult',
    author='Tommy Allen',
    author_email='tommy@esdf.io',
    version=moult.__version__,
    description=description,
    long_description=readme_file('README.md'),
    packages=find_packages(),
    url='https://github.com/tweekmonster/moult',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'moult=moult:main',
            'moult%s=moult:main' % sys.version[:1],
            'moult%s=moult:main' % sys.version[:3],
        ],
    },
    keywords='uninstall remove packages development environment requirements',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    tests_require=['tox'],
    cmdclass={
        'test': Tox,
    }
)
