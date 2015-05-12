#!/usr/bin/env python
"""Wrapper for ELAPS:Viewer."""
from __future__ import division, print_function

# set path to load the lib
import sys
import os
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))
sys.path.append(rootpath)

from elaps.qt import Viewer


def main():
    """Main entry point."""
    reset = "--reset" in sys.argv
    filenames = sys.argv[1:]
    if reset:
        filenames.remove("--reset")
    Viewer(*filenames, reset=reset).start()


if __name__ == "__main__":
    main()
