from . import __version__


def create_argparser():
    import argparse
    from argparse import RawDescriptionHelpFormatter

    description = '''
A utility for finding Python packages that may not be in use.
'''.strip()

    epilog = '''
moult uses `pip` to find installed packages and determine which ones are not
in use. Unfortunately, not all packages install their dependencies for you. In
those cases, pip, and in turn moult, will have no clue. You must use your own
judgment to determine whether or not the packages listed by moult can actually
be removed without affecting your scripts.

Again, moult is helpful for listing packages that *may not* be in use. It is a
convenience and the output should not be blindly trusted.
'''.strip()

    parser = argparse.ArgumentParser(prog='moult', description=description,
                                     epilog=epilog,
                                     formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    parser.add_argument('scan', metavar='scan', nargs='*',
                        help='Scans one or more directories or python files to'
                        ' determine what packages they are using.')

    parser.add_argument('-s', metavar='pkg', nargs='+',
                        dest='packages', required=False, help='Packages to'
                        ' search and check. Can be the package name or import'
                        ' path. Hidden packages can be found, but will not be'
                        ' a suggested removal without the -a flag.')

    parser.add_argument('-l', action='store_true', required=False,
                        dest='local', help='Display local modules only.')

    description = '''Display hidden packages. Packages are hidden if they
installed scripts outside of their package directory, or are hard coded as
packages that aren't likely to be imported by your scripts (virtualenv, pip,
supervisor, etc). When using the -p flag, hidden packages are prefixed with an
underscore so you are less likely to uninstall them on accident.'''

    parser.add_argument('-a', action='store_true', required=False,
                        dest='show_all', help=description)

    parser.add_argument('-f', '--freeze', action='store_true', required=False,
                        dest='freeze', help='Print requirements like pip does,'
                        ' except for scanned files. Requires scanned files to'
                        ' work. If no files or directories are supplied for a'
                        ' scan, the current directory will be scanned.'
                        ' Packages are sorted so that dependencies are'
                        ' installed before dependnat packages. Flags below'
                        ' this are ignored if enabled.')

    parser.add_argument('-r', action='store_true', required=False,
                        dest='recursive', help='Recursively display removable'
                        ' packages.')

    parser.add_argument('-v', action='count', required=False,
                        dest='verbose', help='Set verbosity level. -vv will'
                        ' include debug messages.')

    parser.add_argument('-p', action='store_true', required=False,
                        dest='plain', help='Prints a plain list of removable'
                        ' packages that\'s suitable for copy and paste in the'
                        ' command line. Flags below this are ignored if'
                        ' enabled.')

    parser.add_argument('-d', action='store_true', required=False,
                        dest='detail', help='Display detailed package'
                        ' dependencies.')

    color = parser.add_mutually_exclusive_group()

    color.add_argument('--no-color', action='store_true',
                       required=False, dest='no_color',
                       help='Disable colored output.')

    color.add_argument('--no-colour', action='store_true',
                       required=False, dest='no_colour',
                       help='The classier way to disable colored output.')

    return parser
