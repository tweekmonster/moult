from __future__ import print_function, unicode_literals

import sys
import logging

from . import color

level = logging.WARNING


_log = logging.getLogger('moult')
_log.propagate = False

_level_color = {
    logging.DEBUG: 0,
    logging.INFO: color.FG_BLUE,
    logging.WARN: color.FG_YELLOW,
    logging.ERROR: color.FG_RED,
    logging.FATAL: color.NOOO,
}


debug = _log.debug
info = _log.info
warn = _log.warn
error = _log.error
fatal = _log.fatal
exception = _log.exception


def set_level(level):
    if not level:
        _log.disabled = True
    else:
        _log.setLevel(level)


class ColorOutputHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        c = _level_color.get(record.levelno, 0)
        if record.levelno == logging.DEBUG:
            msg = 'DEBUG: ' + msg
        print(color.ColorText(msg, c), file=sys.stderr)


handler = ColorOutputHandler()
# handler.setFormatter(logging.Formatter('%(message)s'))
_log.addHandler(handler)
_log.setLevel(level)
