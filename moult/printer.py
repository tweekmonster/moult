from __future__ import print_function

import os
import sys
import time

from .utils import running_under_virtualenv
from .color import *
from .exceptions import MoultCommandError
from .compat import str_
from . import __version__


__all__ = ('enable_debug', 'output', 'error', 'wrap', 'print_module')


enable_debug = False
tab_width = 2


def output(*args, **kwargs):
    '''Analog of print() but with an indent option
    '''
    indent = kwargs.pop('indent', 0)
    sep = kwargs.pop('sep', None)
    kwargs['sep'] = u''  # Sanity
    if sep is None:
        sep = u' '
    indent_str = u' ' * (indent * tab_width)
    text = sep.join(map(str_, args))
    color = kwargs.pop('color', None)
    if color:
        color.bright = kwargs.pop('bright', None)
        text = ColorText(text, color)
    print(indent_str + text, **kwargs)


def error(message, fatal=False):
    if fatal:
        raise MoultCommandError(message)
    output(ColorText(message, MEH), file=sys.stderr)


def wrap(items, prefix=0, width=80):
    width -= prefix

    lines = []
    line_i = 0
    line = ColorTextRun()

    for i, item in enumerate(items):
        if i and (line_i - 1 >= width or line_i + len(item) + 1 >= width):
            line_i = 0
            if len(lines):
                indent = u' ' * prefix
            else:
                indent = u''
            lines.append(str_(indent + line).rstrip())
            line = ColorTextRun()

        line += item + ', '
        line_i += 2 + len(item)

    if line:
        if len(lines):
            indent = u' ' * prefix
        else:
            indent = u''
        lines.append(str_(indent + line).rstrip())

    return u'\n'.join(lines).rstrip(', ')


def file_string(filename):
    return ColorTextRun(os.path.dirname(filename),
                        os.path.sep,
                        ColorText(os.path.basename(filename), HEY))


def module_string(pym, require=False, plain=False):
    s = pym.name
    c = NEAT

    if pym.is_scan:
        c = MEH
    elif pym.hidden:
        c = SHHH
    elif pym.local and running_under_virtualenv():
        c = GOOD
    elif not pym.local and running_under_virtualenv():
        c = HEY

    s = ColorText(s, c)

    if pym.hidden and plain:
        s = ColorText(u'_', HEY) + s

    if plain:
        return s

    if require:
        s += ColorTextRun(u'==', ColorText(pym.version, NEAT))
    else:
        s += ColorTextRun(u' (', ColorText(pym.version, NEAT), u')')

    return s


def require_string(pym):
    return module_string(pym, require=True)


def print_requires(pkg, show_all=False, printed=None):
    if printed is None:
        printed = set()

    for dep in pkg.dependencies:
        if not dep.dependants:
            print_requires(dep, show_all=show_all, printed=printed)

    for dep in pkg.dependencies:
        print_requires(dep, show_all=show_all, printed=printed)

    if pkg in printed:
        return

    printed.add(pkg)
    if not pkg.is_scan:
        if pkg.missing:
            output('#', end=' ')
        output(require_string(pkg))


def print_frozen(scans, show_all=False, printed=None):
    output('# Requirements based on scans from:')
    for pym in scans:
        output('#  {}'.format(pym.location))
    date_str = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
    output('# Generated with moult {} at {}'.format(__version__, date_str))

    printed = set()
    for scan in scans:
        print_requires(scan, show_all=show_all, printed=printed)


def print_module(pym, depth=0, indent_str='  ', printed=None, detail=False,
                 show_dependants=False, show_dependencies=False):
    if not printed:
        printed = []

    if pym in printed:
        return

    printed.append(pym)

    output(module_string(pym, not detail), indent=depth)

    if detail:
        loc = u'NOT INSTALLED'
        if pym.is_scan:
            loc = pym.location
        elif pym.local and running_under_virtualenv():
            loc = ColorText(u'VirtualEnv', YAY)
        elif pym.user:
            loc = ColorText(u'User', NEAT)
        elif not pym.missing:
            c = HEY.copy()
            c.set_bright(True)
            loc = ColorText(u'System', c)

        rows = [(u'Location:', [loc])]

        notes = []

        if pym.hidden:
            notes.append(ColorText(u'Hidden Package', SHHH))

        if 'django' in pym.frameworks:
            notes.append(ColorText(u'Contains Django project', NEAT))

        if notes:
            rows.append((u'Notes:', notes))

        if pym.installed_scripts:
            rows.append((u'Scripts:',
                        [file_string(x) for x in pym.installed_scripts]))

        if pym.installed_files:
            rows.append((u'Files:',
                        [file_string(x) for x in pym.installed_files]))

        if pym.dependants:
            rows.append((u'Used In:',
                        [module_string(x) for x in pym.dependants]))

        if not pym.dependencies:
            items = [ColorText(u'None', NEAT)]
        else:
            items = [module_string(x) for x in pym.dependencies]
        rows.append((u'Requires:', items))

        tab = max(map(lambda x: len(x[0]), rows))
        for label, items in rows:
            # Label width, tab width, and space
            w_tab = tab + ((depth + 1) * tab_width) + 1
            output(label.rjust(tab), wrap(items, w_tab), indent=depth + 1)

        print('')

    if show_dependants and pym.dependants:
        for dep in pym.dependants:
            print_module(dep, depth, detail=detail, printed=printed,
                         show_dependencies=show_dependencies)

    if show_dependencies and pym.dependencies:
        for dep in pym.dependencies:
            print_module(dep, depth, detail=detail, printed=printed,
                         show_dependencies=show_dependencies)
