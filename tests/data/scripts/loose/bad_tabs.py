#!/usr/bin/env python

# This script should still be scannable.  Moult is not the syntax police.
import os
    import sys
from moult import VERSION

                sys.stdout.write('Moult Version: %s' % VERSION)

# This script should never execute when scanned
directory = '../readonly'
for filename in os.listdir(directory):
os.remove(os.path.join(directory, filename))
