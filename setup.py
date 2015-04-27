import sys

from setuptools import setup

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

setup(
    name='moult',
    author='Tommy Allen',
    author_email='tommy@esdf.io',
    version=moult.VERSION,
    description=description,
    long_description=readme_file('README.md'),
    packages=['moult'],
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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
