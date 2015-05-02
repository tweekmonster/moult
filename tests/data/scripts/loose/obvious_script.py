#!/usr/bin/env python
# This script is obvious because it ends with .py
import os
import sys
from moult import VERSION

sys.stdout.write('Moult Version: %s' % VERSION)

# This script should never execute when scanned
directory = '../readonly'
for filename in os.listdir(directory):
    os.remove(os.path.join(directory, filename))
