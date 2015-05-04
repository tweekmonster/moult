#!/usr/bin/env python
# Note there is no coding
# こんにちは！
import os
import sys
from moult import __version__
from 脱皮 import それが壊れていました

sys.stdout.write('脱皮バージョン: %s' % __version__)

# This script should never execute when scanned
directory = '../readonly'
for filename in os.listdir(directory):
    os.remove(os.path.join(directory, filename))
