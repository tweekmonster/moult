import sys

PY3 = sys.version_info[0] == 3

str_ = str
if not PY3:
    str_ = unicode  # noqa
