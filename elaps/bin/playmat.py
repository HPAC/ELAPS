#!/usr/bin/env python
"""Wrapper for ELAPS:PlayMat."""
from __future__ import division, print_function

from .. import defines
from ..qt import PlayMat

import argparse


def main():
    """Main entry point."""
    # parse args
    parser = argparse.ArgumentParser(
        description="ELAPS PlayMat (Experiment GUI)"
    )
    parser.add_argument("--reset", action="store_true",
                        help="reset to default Experiment")
    parser.add_argument(
        "experiment",  nargs="?",
        help="An ELAPS Experiment (.%s) or Report (.%s)" %
        (defines.experiment_extension, defines.report_extension)
    )
    args = parser.parse_args()

    # start PlayMat
    PlayMat(load=args.experiment, reset=args.reset).start()

if __name__ == "__main__":
    main()
