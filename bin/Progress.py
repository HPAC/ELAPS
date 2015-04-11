#!/usr/bin/env python
"""Execute ELAPS:Experiments."""
from __future__ import division, print_function

# set path to load the lib
import sys
import os
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))
sys.path.append(rootpath)

import elaps.io
import elaps.defines as defines


def main():
    """Main entry point."""
    jobs = []
    for filename in sys.argv[1:]:
        # load experiment
        try:
            fin = open(filename)
            ex = elaps.io.load_experiment_string(fin.readline())
            nresults = ex.nresults()
        except:
            print("ERROR: Can't load %r" % filename, file=sys.stderr)
            continue
        progress = min(nresults, len(fin.readlines()) - 1)

        print("%s:\t%d/%d\t(%d %%)" % (filename, progress, nresults,
                                       100 * progress // nresults))

if __name__ == "__main__":
    main()
