# Moult

[![Build Status](https://travis-ci.org/tweekmonster/moult.svg?branch=develop)](https://travis-ci.org/tweekmonster/moult)

Moult is a utility that can assist you in finding packages that may not be in use any more. It was created to help me clean up a project's requirements.txt file after a major overhaul. It's far from perfect, but it's a lot faster than figuring out what's actually needed in a `pip freeze` print out.

## Requirements

* `Python 2.7+`
* `pip 1.3+` is required, but is not listed as a dependency so you aren't forced to upgrade your installed version.

## Installation

Since you definitely have pip installed, you can run: `pip install moult`

## Handy Features

* Can be installed globally and ran in Virtual Environments
* Displays package dependencies
* Suggests packages that can be removed
* Search for installed packages using their package name or import path
* Scan your project directories or files to see what packages they are using
* Detects and loads Django settings to see what optional packages are in use

## Command Line Interface:

```
usage: moult [-h] [-V] [-s pkg [pkg ...]] [-l] [-a] [-f] [-r] [-v] [-p] [-d]
             [--no-color | --no-colour]
             [scan [scan ...]]

A utility for finding Python packages that may not be in use.

positional arguments:
  scan              Scans one or more directories or python files to determine
                    what packages they are using.

optional arguments:
  -h, --help        show this help message and exit
  -V, --version     show program's version number and exit
  -s pkg [pkg ...]  Packages to search and check. Can be the package name or
                    import path. Hidden packages can be found, but will not be
                    a suggested removal without the -a flag.
  -l                Display local modules only.
  -a                Display hidden packages. Packages are hidden if they
                    installed scripts outside of their package directory, or
                    are hard coded as packages that aren't likely to be
                    imported by your scripts (virtualenv, pip, supervisor,
                    etc). When using the -p flag, hidden packages are prefixed
                    with an underscore so you are less likely to uninstall
                    them on accident.
  -f, --freeze      Print requirements like pip does, except for scanned
                    files. Requires scanned files to work. If no files or
                    directories are supplied for a scan, the current directory
                    will be scanned. Packages are sorted so that dependencies
                    are installed before dependnat packages. Flags below this
                    are ignored if enabled.
  -r                Recursively display removable packages.
  -v                Set verbosity level. -vv will include debug messages.
  -p                Prints a plain list of removable packages that's suitable
                    for copy and paste in the command line. Flags below this
                    are ignored if enabled.
  -d                Display detailed package dependencies.
  --no-color        Disable colored output.
  --no-colour       The classier way to disable colored output.

moult uses `pip` to find installed packages and determine which ones are not
in use. Unfortunately, not all packages install their dependencies for you. In
those cases, pip, and in turn moult, will have no clue. You must use your own
judgment to determine whether or not the packages listed by moult can actually
be removed without affecting your scripts.

Again, moult is helpful for listing packages that *may not* be in use. It is a
convenience and the output should not be blindly trusted.
```
