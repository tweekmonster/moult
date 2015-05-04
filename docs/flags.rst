********************
Command Line Options
********************

.. code-block:: none

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


Detailed Explanations
=====================

Some options that need a little more explanation than what the help output
provides.

**scan**
    Optional positional arguments consisting of directories or files you want
    to scan. The printed results will list used packages under the top level
    directory or script names in your scan.

    Files are scanned for import statements and matched against installed
    packages. If no installed package is found, the import is silently ignored.

    If a :file:`settings.py` file is encountered and contains an
    ``INSTALLED_APPS`` variable, :command:`moult` will attempt to load it as a
    Django project to determine the project's configured package dependencies.
    :command:`moult` will first attempt to use Django's
    `apps <https://docs.djangoproject.com/en/1.8/ref/applications/>`_
    registry to get the installed apps. If it fails, it will fall back to
    directly reading the ``INSTALLED_APPS`` variable. Any complication in
    loading the settings will be printed to the console.

**-s**
    Search for a package. You can supply either the package name or import path
    of a module. When searching for an import path, moult will find the package
    that defines a top level module matching the import path.

**-l**
    If you created a virutalenv with the :option:`--system-site-packages`
    flag, this means that the system's site-packages are visible to
    :command:`pip` and :command:`moult`. Enabling this flag tells
    :command:`moult` to ignore packages that exist outside of your virtualenv.

.. _show-all:

**-a**
    Enabling this flag will display hidden packages. Packages are hidden
    either by :command:`pip`'s hard coded ignored packages or if they have
    installed scripts that exist out side of the package's import path. Extra
    package files are considered scripts if they contain a shebang (#!) in the
    first 2 bytes of the file. It is assumed that if a package installed
    scripts, the package's purpose goes beyond being imported in your scripts.
    When combined with the :option:`-p` flag, package names will be prefixed
    with an underscore to avoid accidental removals if you eagerly copy and
    pasted the output when running :command:`pip uninstall`.
