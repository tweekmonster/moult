'''A utility for finding Python packages that may not be in use.
'''
from __future__ import print_function

import os
import sys
import codecs


__all__ = ('__version__', 'main')
__version__ = '0.1.2'


if sys.stdout.encoding is None:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
if sys.stderr.encoding is None:
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)


def is_venv():
    '''Redefinition of pip's running_under_virtualenv().
    '''
    return hasattr(sys, 'real_prefix') \
        or sys.prefix != getattr(sys, 'base_prefix', sys.prefix)


def main():
    if 'VIRTUAL_ENV' in os.environ and not is_venv():
        # Activate the virtualenv before importing moult's program to avoid
        # loading modules.
        print('Activating', os.environ['VIRTUAL_ENV'])
        activate = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'activate_this.py')
        if os.path.exists(activate):
            with open(activate) as fp:
                exec(compile(fp.read(), activate, 'exec'), {'__file__': activate})

    from moult.program import run
    return run()
