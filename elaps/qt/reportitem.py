#!/usr/bin/env python
"""Report list entry in the Viewer."""
from __future__ import division, print_function

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot


class QReportItem(QtGui.QTreeWidgetItem):

    """Report list entry (Viewer)."""

    def __init__(self, viewer, filename, report, callid=None):
        """Init the report element."""
        QtGui.QTreeWidgetItem.__init__(self)

        ex = report.experiment

        self.viewer = viewer
        self.filename = filename
        self.callid = callid
        self.report = report
        self.experiment = ex
        self.reportname = os.path.basename(filename)[:-4]
        self.callname = None
        self.plotlabel = self.reportname
        if callid is not None:
            self.callname = ex.calls[callid][0]
            self.plotlabel = "%s[%s] (%s)" % (self.reportname, callid,
                                              self.callname)
        self.children = []
        self.showing = callid is None
        self.color = viewer.colors.pop()

        self.UI_init()

        # children
        if callid is None and len(self.experiment.calls) > 1:
            for callid in range(len(ex.calls)):
                child = QReportItem(viewer, filename, report, callid)
                self.children.append(child)
                self.addChild(child)

    def close(self):
        """Clear: Return colors to viewer."""
        for UI_item in reversed(self.children):
            self.viewer.colors.append(UI_item.color)
        self.viewer.colors.append(self.color)

    def UI_init(self):
        """Init the UI elements."""
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if self.callid is None:
            flags = flags | QtCore.Qt.ItemIsDragEnabled
        self.setFlags(flags)

    def UI_setall(self):
        """Set all UI elements."""
        if self.callid is None:
            self.setText(0, self.reportname)
            self.setToolTip(0, os.path.relpath(self.filename))
        else:
            self.setText(0, self.callname)
            self.setToolTip(0, str(self.report.experiment.calls[self.callid]))

        # generate/set widgets
        if self.viewer.UI_reports.itemWidget(self, 1) is None:
            self.UI_showing = QtGui.QCheckBox(toggled=self.on_showing_change)
            self.viewer.UI_reports.setItemWidget(self, 1, self.UI_showing)
        if self.viewer.UI_reports.itemWidget(self, 2) is None:
            self.UI_color = QtGui.QPushButton(clicked=self.on_color_change)
            self.viewer.UI_reports.setItemWidget(self, 2, self.UI_color)
        if self.viewer.UI_reports.itemWidget(self, 3) is None:
            self.UI_plotlabel = QtGui.QLineEdit(
                textChanged=self.on_plotlabel_change
            )
            self.viewer.UI_reports.setItemWidget(self, 3, self.UI_plotlabel)

        # set widget values
        self.UI_showing.setChecked(self.showing)
        self.UI_color.pyqtConfigure(
            styleSheet="background-color: %s;" % self.color,
            text=self.color
        )
        self.UI_plotlabel.setText(self.plotlabel)

        for child in self.children:
            child.UI_setall()

    # Events
    @pyqtSlot(bool)
    def on_showing_change(self, checked):
        """Event: showing changed."""
        if self.viewer.UI_setting:
            return
        self.showing = checked
        self.viewer.UI_plot_set()

    @pyqtSlot()
    def on_color_change(self):
        """Event: change color."""
        if self.viewer.UI_setting:
            return
        Qcolor = QtGui.QColorDialog.getColor(QtGui.QColor(
            self.color
        ))
        if Qcolor.isValid():
            self.color = str(Qcolor.name())
        self.UI_setall()
        self.viewer.UI_plot_set()

    @pyqtSlot(str)
    def on_plotlabel_change(self, value):
        """Event: plotlabel changed."""
        if self.viewer.UI_setting:
            return
        self.plotlabel = str(value)
        self.viewer.UI_plot_set()
