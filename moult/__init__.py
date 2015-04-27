'''A utility for finding Python packages that may not be in use.
'''
import os
import sys
import codecs

from .version import VERSION


__all__ = ('VERSION', 'main')


if sys.stdout.encoding is None:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
if sys.stderr.encoding is None:
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)


def main():
    if 'VIRTUAL_ENV' in os.environ:
        activate = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'activate_this.py')
        if os.path.exists(activate):
            try:
                execfile(activate, {'__file__': activate})
            except NameError:
                with open(activate) as fp:
                    exec(compile(fp.read(), activate, 'exec'), {'__file__': activate})

    from moult.program import run
    return run()
