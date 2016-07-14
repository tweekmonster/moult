from __future__ import unicode_literals

import sys

from .compat import PY3, str_


FG_BLACK = 30
FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_MAGENTA = 35
FG_CYAN = 36
FG_WHITE = 37
FG_RESET = 39

BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_WHITE = 47
BG_RESET = 49


enabled = True
_enabled = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ColorCombo(object):
    def __init__(self, foreground=0, background=0, bright=None):
        self.foreground = foreground or FG_RESET
        self.background = background or BG_RESET
        self.set_bright(bright)

    def set_bright(self, bright):
        if bright is None:
            self.flag = 22
        elif bright:
            self.flag = 1
        else:
            self.flag = 2

    def copy(self):
        c = ColorCombo(self.foreground, self.background)
        c.flag = self.flag
        return c

    def __repr__(self):
        r = '<ColorCombo [{:d}, {:d}]>'.format(self.foreground, self.background)
        if PY3:
            return r
        return r.encode('utf8')


HEY = ColorCombo(FG_RED)
YAY = ColorCombo(FG_GREEN)
MEH = ColorCombo(FG_YELLOW)
GOOD = ColorCombo(FG_BLUE)
NEAT = ColorCombo(FG_CYAN)
SHHH = ColorCombo(FG_MAGENTA)
NOOO = ColorCombo(FG_WHITE, BG_RED, bright=True)
MAN = ColorCombo(FG_BLACK, BG_YELLOW, bright=True)


class ColorTextRun(object):
    '''String imposter that supports multiple color strings, mostly so len()
    reports the actual text's length
    '''
    def __init__(self, *items):
        self.items = list(items)

    def __len__(self):
        return sum(map(len, self.items))

    def __unicode__(self):
        return str_(''.join(map(str_, self.items)))

    def __str__(self):
        if PY3:
            return self.__unicode__()
        return self.__unicode__().encode('utf8')

    def __repr__(self):
        r = '<ColorTextRun {}>'.format([repr(x) for x in self.items])
        if PY3:
            return r
        return r.encode('utf8')

    def __add__(self, other):
        self.items.append(other)
        return self

    def __radd__(self, other):
        self.items.insert(0, other)
        return self

    def encode(self, *args, **kwargs):
        return str_(self).encode(*args, **kwargs)

    def decode(self, *args, **kwargs):
        return str_(self).decode(*args, **kwargs)


class ColorText(object):
    '''String imposter that supports colored strings, mostly so len()
    reports the actual text's length
    '''
    fmt = '\033[{fg:d};{bg:d};{f}m{t}\033[0m'

    def __init__(self, text, foreground=0, background=0, ignore_setting=False):
        self.text = text
        if isinstance(foreground, ColorCombo):
            self.color = foreground
        else:
            self.color = ColorCombo(foreground or FG_RESET,
                                    background or BG_RESET)
        self.ignore_setting = ignore_setting

    def __len__(self):
        return len(self.text)

    def __unicode__(self):
        if not _enabled or (not self.ignore_setting and not enabled):
            return self.text
        return self.fmt.format(fg=self.color.foreground,
                               bg=self.color.background,
                               f=self.color.flag,
                               t=self.text)

    def __str__(self):
        if PY3:
            return str_(self.__unicode__())
        return self.__unicode__().encode('utf8')

    def __repr__(self):
        r = '<ColorText "{}" ({})>'.format(self.text, repr(self.color))
        if PY3:
            return r
        return r.encode('utf8')

    def __add__(self, other):
        return ColorTextRun(self, other)

    def __radd__(self, other):
        return ColorTextRun(other, self)

    def encode(self, *args, **kwargs):
        return str_(self).encode(*args, **kwargs)

    def decode(self, *args, **kwargs):
        return str_(self).decode(*args, **kwargs)
