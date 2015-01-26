#!/usr/bin/env python
from __future__ import division, print_function

from viewerqt import Viewer_Qt
from qmplplot import QMPLPlot

import sys


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    loadstate = "--reset" not in sys.argv[1:]
    Viewer_Qt(QMPLPlot, loadstate)

if __name__ == "__main__":
    main()
