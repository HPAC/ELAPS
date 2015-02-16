#!/usr/bin/env python
from __future__ import division, print_function

from qt_viewer import QViewer
from qt_mpl_plot import QMPLPlot

import sys


class QMPLViewer(QViewer):
    def __init__(self, app=None, loadstate=True):
        QViewer.__init__(self, QMPLPlot, app, loadstate)


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    loadstate = "--reset" not in sys.argv[1:]
    QMPLViewer(loadstate=loadstate).start()

if __name__ == "__main__":
    main()
