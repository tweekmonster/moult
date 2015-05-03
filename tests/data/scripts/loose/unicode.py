#!/usr/bin/env python
# Note there is no coding
# こんにちは！
import os
import sys
from moult import VERSION

sys.stdout.write('脱皮バージョン: %s' % VERSION)

# This script should never execute when scanned
directory = '../readonly'
for filename in os.listdir(directory):
    os.remove(os.path.join(directory, filename))
