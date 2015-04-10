#!/usr/bin/env python
"""Wrapper for ELAPS:PlayMat."""
from __future__ import division, print_function

# set path to load the lib
import sys
import os
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))
sys.path.append(rootpath)

from elaps.qt import PlayMat


def main():
    """Main entry point."""
    if "--reset" in sys.argv:
        PlayMat(reset=True).start()
        return
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename[-4:] in (".ees", ".eer"):
            PlayMat(load=filename).start()
            return
    PlayMat().start()


if __name__ == "__main__":
    main()
