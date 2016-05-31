#!/usr/bin/env python
"""Show ELAPS:Report progress."""
from __future__ import division, print_function

from .. import defines
from .. import io as elapsio

import argparse


def main():
    """Main entry point."""
    # parse args
    parser = argparse.ArgumentParser(
        description="Show ELAPS Report progress"
    )
    parser.add_argument("report",  nargs="+",
                        help="ELAPS Report (.%s)" % defines.report_extension)
    args = parser.parse_args()

    for filename in args.report:
        # load experiment
        try:
            fin = open(filename)
            ex = elapsio.load_experiment_string(fin.readline())
        except:
            print("ERROR: Can't load %r" % filename, file=sys.stderr)
            continue
        nresults = ex.nresults()
        progress = min(nresults, len(fin.readlines()) - 1)

        # print progress
        print("%s:\t%d/%d\t(%d %%)" % (filename, progress, nresults,
                                       100 * progress // nresults))

if __name__ == "__main__":
    main()
