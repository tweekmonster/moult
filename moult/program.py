from __future__ import print_function

from .args import create_argparser
from .exceptions import MoultCommandError
from . import color, printer, filesystem_scanner, utils, log


def more_turtles(packages, show_all=False):
    remove = []
    for pym in packages:
        if not show_all and pym.hidden:
            continue
        if not pym.missing and not pym.is_scan and not len(pym._dependants):
            remove.append(pym)

    return remove


def moult(packages=None, detail=False, scan=None, local=False, recursive=False,
          plain=False, show_all=False, freeze=False, **kwargs):
    installed = utils.installed_packages(local=local)

    if packages is None:
        packages = []

    if freeze and not scan:
        scan = ['.']

    if scan:
        header_printed = False

        for d in scan:
            pym = filesystem_scanner.scan(d, installed)

            if not freeze and pym:
                if not header_printed:
                    printer.output('Found in scan:', color=color.YAY)
                    header_printed = True
                printer.print_module(pym, detail=True, depth=1)

    if freeze:
        scans = [s for s in installed if s.is_scan]
        printer.print_frozen(scans, show_all=show_all)
        return

    displaying = []
    if packages:
        for pkg in packages:
            pym = utils.find_package(pkg, installed, True)
            if pym:
                displaying.append(pym)
            else:
                import_parts = pkg.split('.')
                for i in range(len(import_parts), 0, -1):
                    pym = utils.find_package('.'.join(import_parts[:i]), installed)
                    if pym:
                        displaying.append(pym)
                        break

        if not displaying:
            log.error('No matching packages: %s', ', '.join(packages))
            return

    if not displaying:
        displaying = installed[:]
    else:
        printer.output('Matched modules:', color=color.YAY)
        for pym in displaying:
            printer.print_module(pym, detail=True, depth=1)
        print('')

    removable = more_turtles(displaying, show_all)
    if not removable:
        printer.output('Nothing to remove', color=color.YAY, end='\n\n')
        return

    if removable:
        i = 0

        while len(removable):
            if not i:
                printer.output('Packages that can be removed:', color=color.YAY)
            else:
                printer.output('Then you could remove:', color=color.YAY)

            next_packages = []

            for pym in removable:
                if plain:
                    print(printer.module_string(pym, plain=True), end=' ')
                else:
                    printer.print_module(pym, detail=detail, depth=1)

                for dep in pym.dependencies:
                    dep.remove_dependant(pym)
                    if dep not in next_packages:
                        next_packages.append(dep)

            if plain:
                print('\n')
            else:
                print('')

            if not recursive:
                break

            removable = more_turtles(next_packages, show_all)
            i += 1


def run():
    parser = create_argparser()
    args = parser.parse_args()

    if args.no_color or args.no_colour:
        color.enabled = False

    if args.verbose:
        log.set_level(log.level - min(args.verbose, 2) * 10)

    if args.freeze:
        log.set_level(0)
        color.enabled = False

    exit_code = 0

    try:
        moult(**vars(args))
    except MoultCommandError as e:
        exit_code = 1
        log.fatal('Error: %s', e)
    except KeyboardInterrupt:
        exit_code = 1
        import getpass
        print('\n{}, eat a snickers'.format(getpass.getuser()))
    finally:
        if not utils.running_under_virtualenv():
            printer.output('/!\\ You are not in a Virtual Environment /!\\',
                           color=color.MAN)

    return exit_code
