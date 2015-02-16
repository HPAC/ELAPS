#!/usr/bin/env python
from __future__ import division, print_function

from mpl_plot import MPLPlot

from PyQt4 import QtGui
import matplotlib.backends.backend_qt4agg as QtMPL


class QMPLPlot(MPLPlot, QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self)
        MPLPlot.__init__(self)
        self.UI_init()
        if args:
            self.plot(*args)

    def UI_init(self):
        # layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # canvas
        self.Qcanvas = QtMPL.FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.Qcanvas, 1)

        # toolbar
        toolbarL = QtGui.QHBoxLayout()
        layout.addLayout(toolbarL)
        self.Qtoolbar = QtMPL.NavigationToolbar2QT(self.Qcanvas, self)
        toolbarL.addWidget(self.Qtoolbar)

    def UI_update(self):
        self.setWindowTitle(self.title)
        self.Qcanvas.draw()
