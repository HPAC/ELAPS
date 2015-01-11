#!/usr/bin/env python
from __future__ import division, print_function

from viewer import Viewer

import sys

from PyQt4 import QtCore, QtGui


class Viewer_Qt(Viewer, QtGui.QApplication):
    state = {}

    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        self.setting = False
        Viewer.__init__(self)

    def UI_init(self):
        # window
        self.Qt_window = QtGui.QWidget()
        self.Qt_window.setWindowTitle("Viewer")
        windowL = QtGui.QHBoxLayout()
        self.Qt_window.setLayout(windowL)

        # reports
        reportL = QtGui.QVBoxLayout()
        windowL.addLayout(reportL)

        # load
        icon = self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton)
        load = QtGui.QPushButton(icon, "&open repot")
        reportL.addWidget(load)
        load.clicked.connect(self.Qt_load_click)

        # report list
        self.Qt_reports = QtGui.QTreeWidget()
        reportL.addWidget(self.Qt_reports, 1)
        self.Qt_reports.setHeaderLabels(("report", "", "sytem", "#t", "blas",
                                         "range"))
        self.Qt_reports.setMinimumWidth(400)
        self.Qt_reports.currentItemChanged.connect(self.Qt_report_select)
        self.Qt_reports.itemExpanded.connect(self.Qt_report_expanded)

        # right
        rightL = QtGui.QVBoxLayout()
        windowL.addLayout(rightL)

        # info
        info = QtGui.QGroupBox()
        rightL.addWidget(info)
        infoL = QtGui.QVBoxLayout()
        info.setLayout(infoL)
        self.Qt_info = QtGui.QLabel()
        infoL.addWidget(self.Qt_info)
        infoL.addStretch(1)

        # plotting
        showplot = QtGui.QPushButton("show &plot")
        rightL.addWidget(showplot)
        showplot.clicked.connect(self.Qt_showplot_click)

        # window
        self.Qt_columns_resize()
        self.Qt_window.show()

    def UI_start(self):
        sys.exit(self.exec_())

    def Qt_columns_resize(self):
        for colid in range(self.Qt_reports.columnCount()):
            self.Qt_reports.resizeColumnToContents(colid)

    # setters
    def UI_report_add(self, reportid):
        report = self.reports[reportid]
        sampler = report["sampler"]

        #  tree item
        rangestr = ""
        if report["userange"]:
            rangestr = "%d:%d:%d" % (
                report["range"][0],
                report["range"][2],
                report["range"][1] - 1
            )
        Qreport = QtGui.QTreeWidgetItem((
            report["name"],
            "",
            sampler["system_name"],
            str(report["nt"]),
            sampler["blas_name"],
            rangestr,
        ))
        self.Qt_reports.addTopLevelItem(Qreport)
        Qreport.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        # tooltips
        Qreport.setToolTip(0, report["filename"])
        Qreport.setToolTip(2, sampler["cpu_model"])

        # checkbox
        Qcheck = QtGui.QCheckBox()
        self.Qt_reports.setItemWidget(Qreport, 1, Qcheck)
        Qcheck.setChecked(True)
        Qcheck.stateChanged.connect(self.Qt_reportcheck_change)
        Qcheck.item = Qreport

        # annotate
        Qreport.reportid = reportid
        Qreport.callid = None

        for callid, call in enumerate(report["calls"]):
            Qitem = QtGui.QTreeWidgetItem((call[0],))
            Qreport.addChild(Qitem)

            # tooltip
            Qitem.setToolTip(0, str(call))

            # checkbox
            Qcheck = QtGui.QCheckBox()
            self.Qt_reports.setItemWidget(Qitem, 1, Qcheck)
            Qcheck.stateChanged.connect(self.Qt_reportcheck_change)
            Qcheck.item = Qitem

            # annotate
            Qitem.reportid = reportid
            Qitem.callid = callid
        self.Qt_columns_resize()

    def UI_info_set(self, infostr):
        self.Qt_info.setText(infostr)

    # event handlers
    def Qt_load_click(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            self.Qt_window,
            "open report",
            self.reportpath,
            "*.smpl"
        )
        filename = str(filename)
        if filename:
            self.UI_load_report(filename)

    def Qt_report_expanded(self, item):
        self.Qt_reports.resizeColumnToContents(0)

    def Qt_report_select(self, item):
        self.UI_report_select(item.reportid, item.callid)

    def Qt_reportcheck_change(self):
        sender = self.sender()
        self.UI_reportcheck_change(sender.item.reportid, sender.item.callid,
                                   sender.isChecked())

    def Qt_showplot_click(self):
        self.UI_showplot_click()


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Viewer_Qt()


if __name__ == "__main__":
    main()
