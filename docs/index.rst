*****
Moult
*****

A utility for finding Python packages that may not be in use.

When you uninstall a package via :program:`pip`, you will be left with its dependency
packages (for good reason). It's not the end of the world, but in projects
where you want to maintain a :file:`requirements.txt` file by using the output of
:program:`pip freeze`, it can be pretty frustrating to figure out which one of the
packages is actually used by your project or the packages your project depends
on.

Moult can help by scanning your project files and printing the packages that
appears to have no relation to your project.

.. toctree::
    :maxdepth: 2

    flags.rst
    crashcourse.rst


Links
=====

* PyPI: `<https://pypi.python.org/pypi/moult/>`_
* Source Code: `<https://github.com/tweekmonster/moult>`_
