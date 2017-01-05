#!/usr/bin/env python
"""Show ELAPS:Experiments."""

from __future__ import print_function

import sys
import argparse

from .. import defines
from .. import io as elapsio


def main():
    """Main entry point."""
    # parse args
    parser = argparse.ArgumentParser(
        description="Show ELAPS Experiments and Reports"
    )
    parser.add_argument(
        "item",  nargs="+",
        help="ELAPS Experiment (%s) or Report (.%s)" %
        (defines.experiment_extension, defines.report_extension)
    )
    args = parser.parse_args()

    for filename in args.item:
        # load experiment
        try:
            ex = elapsio.load_experiment(filename)
        except:
            print("ERROR: Can't load %r" % filename, file=sys.stderr)
            continue

        # print experiment
        if len(args.item) > 1:
            print("%s:" % filename)
        print(ex)

if __name__ == "__main__":
    main()
