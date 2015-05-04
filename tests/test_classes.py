# coding: utf8
from __future__ import unicode_literals

from moult.classes import PyModule
from moult.color import ColorCombo, ColorText, ColorTextRun


def test_repr():
    c1 = ColorCombo(5)
    c2 = ColorText('हरामी', c1)
    c3 = ColorTextRun('हरामी', c2)
    c4 = PyModule('हरामी', 'test', 'test')

    repr(c1)
    repr(c2)
    repr(c3)
    repr(c4)
