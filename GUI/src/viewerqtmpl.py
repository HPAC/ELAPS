#!/usr/bin/env python
from __future__ import division, print_function

from viewerqt import Viewer_Qt
from qmplplot import QMPLPlot

import sys


class Viewer_Qt_MPL(Viewer_Qt):
    def __init__(self, app=None, loadstate=True):
        Viewer_Qt.__init__(self, QMPLPlot, app, loadstate)


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    loadstate = "--reset" not in sys.argv[1:]
    Viewer_Qt_MPL(loadstate=loadstate).start()

if __name__ == "__main__":
    main()
