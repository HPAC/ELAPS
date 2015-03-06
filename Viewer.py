#!/usr/bin/env python
"""Wrapper for ELAPS:Viewer."""
from __future__ import division, print_function

from elaps.qt import Viewer

import sys


def main():
    """Main entry point."""
    reset = "--reset" in sys.argv
    filenames = sys.argv[1:]
    if reset:
        filenames.remove("--reset")
    Viewer(*filenames, reset=reset).start()


if __name__ == "__main__":
    main()
