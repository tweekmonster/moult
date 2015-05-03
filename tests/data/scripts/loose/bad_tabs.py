#!/usr/bin/env python

# This script should still be scannable.  Moult is not the syntax police.
import os, moult
import (
    os, moult,
    testpackage
)
    import sys
from moult import VERSION

                    from moult.utils import
(     ham,
        spam, eggs,

        cheese as Red_Leicester ,
 bacon,
            )

                sys.stdout.write('Moult Version: %s' % VERSION)

# This script should never execute when scanned
directory = '../readonly'
for filename in os.listdir(directory):
os.remove(os.path.join(directory, filename))
