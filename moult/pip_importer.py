from __future__ import print_function

from .exceptions import MoultCommandError

try:
    # pip >= 6.0
    from pip.utils import (dist_is_local, dist_in_usersite,
                           get_installed_distributions,
                           running_under_virtualenv)
except ImportError:
    try:
        # pip >= 1.3
        from pip.util import (dist_is_local, dist_in_usersite,
                              get_installed_distributions,
                              running_under_virtualenv)
    except ImportError:
        raise MoultCommandError('Could not import pip functions')


# More packages that most likely wouldn't be used by other packages.
# They're listed here in case they weren't installed normally.
ignore_packages = (
    'setuptools',
    'pip',
    'python',
    'distribute',
    'virtualenv',
    'virtualenvwrapper',
    'ipython',
    'supervisor',
)


__all__ = ('dist_is_local', 'dist_in_usersite', 'get_installed_distributions',
           'running_under_virtualenv', 'ignore_packages')
