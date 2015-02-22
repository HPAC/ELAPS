#!/usr/bin/env python
"""Qt and matplotlib implementaiton of ELAPS:Viewer."""
from __future__ import division, print_function

from qt_viewer import QViewer
from qt_mpl_plot import QMPLPlot

import sys


class QMPLViewer(QViewer):

    """ELAPS:Viwer implementation in Qt and matplotlib."""

    def __init__(self, app=None, loadstate=True):
        """Initialize the ELAPS:Viewer."""
        QViewer.__init__(self, QMPLPlot, app, loadstate)


def main():
    """Main routine to start a Qt and matplotlib based Viewer."""
    loadstate = "--reset" not in sys.argv[1:]
    QMPLViewer(loadstate=loadstate).start()

if __name__ == "__main__":
    main()
