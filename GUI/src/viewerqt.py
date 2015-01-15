#!/usr/bin/env python
from __future__ import division, print_function

from viewer import Viewer

import sys

from PyQt4 import QtCore, QtGui


class Viewer_Qt(Viewer, QtGui.QApplication):
    def __init__(self, plotfactory):
        self.plotfactory = plotfactory
        QtGui.QApplication.__init__(self, sys.argv)
        self.setting = False
        Viewer.__init__(self)

    def UI_init(self):
        self.UI_hasHTML = True

        # window
        self.Qt_window = QtGui.QWidget()
        self.Qt_window.setWindowTitle("Viewer")
        windowL = QtGui.QHBoxLayout()
        self.Qt_window.setLayout(windowL)

        # left
        leftL = QtGui.QVBoxLayout()
        windowL.addLayout(leftL)
        leftL.setContentsMargins(0, 0, 0, 0)

        # reports
        reports = QtGui.QGroupBox("reports")
        leftL.addWidget(reports)
        reportsL = QtGui.QVBoxLayout()
        reports.setLayout(reportsL)

        # load
        icon = self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton)
        load = QtGui.QPushButton(icon, "&load")
        reportsL.addWidget(load)
        load.clicked.connect(self.Qt_load_click)

        # report list
        self.Qt_reports = QtGui.QTreeWidget()
        reportsL.addWidget(self.Qt_reports, 1)
        self.Qt_reports.setHeaderLabels(("report", "", "color", "sytem", "#t",
                                         "blas", "range"))
        self.Qt_columns_resize()
        self.Qt_reports.setMinimumWidth(400)
        self.Qt_reports.currentItemChanged.connect(self.Qt_report_select)
        self.Qt_reports.itemExpanded.connect(self.Qt_report_expanded)

        # metric selection
        metrics = QtGui.QGroupBox("metrics")
        leftL.addWidget(metrics)
        metricsL = QtGui.QVBoxLayout()
        metrics.setLayout(metricsL)
        metricselectL = QtGui.QHBoxLayout()
        metricsL.addLayout(metricselectL)

        # metric list
        self.Qt_metricslist = QtGui.QComboBox()
        metricselectL.addWidget(self.Qt_metricslist)
        self.Qt_metricslist.addItems(sorted(self.metrics.keys()))
        self.Qt_metricslist.currentIndexChanged.connect(
            self.Qt_metricselect_change
        )

        # plot
        metricplot = QtGui.QPushButton("&plot")
        metricselectL.addWidget(metricplot)
        metricplot.clicked.connect(self.Qt_plot_clicked)
        metricselectL.addStretch(1)

        # metricinfo
        metricinfobox = QtGui.QGroupBox()
        metricinfobox.setContentsMargins(0, 0, 0, 0)
        metricsL.addWidget(metricinfobox)
        metricinfoL = QtGui.QVBoxLayout()
        metricinfobox.setLayout(metricinfoL)
        self.Qt_metricinfo = QtGui.QLabel()
        metricinfoL.addWidget(self.Qt_metricinfo)

        # report info
        reportinfobox = QtGui.QGroupBox()
        windowL.addWidget(reportinfobox)
        reportinfoL = QtGui.QVBoxLayout()
        reportinfobox.setLayout(reportinfoL)
        self.Qt_reportinfo = QtGui.QLabel()
        reportinfoL.addWidget(self.Qt_reportinfo)
        reportinfoL.addStretch(1)

        # Qt objects
        self.Qt_Qreports = {}
        self.Qt_Qplots = {}

        # select metric
        self.Qt_metricslist.setCurrentIndex(
            self.Qt_metricslist.findText(self.metric_selected)
        )

    def UI_start(self):
        self.Qt_window.show()
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
            "",
            sampler["system_name"],
            str(report["nt"]),
            sampler["blas_name"],
            rangestr,
        ))
        self.Qt_reports.addTopLevelItem(Qreport)
        self.Qt_Qreports[reportid] = Qreport
        Qreport.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        # tooltips
        Qreport.setToolTip(0, report["filename"])
        Qreport.setToolTip(3, sampler["cpu_model"])

        # checkbox
        Qcheck = QtGui.QCheckBox()
        self.Qt_reports.setItemWidget(Qreport, 1, Qcheck)
        Qreport.checkbox = Qcheck
        Qcheck.stateChanged.connect(self.Qt_reportcheck_change)
        Qcheck.item = Qreport

        # colorbutton
        Qbutton = QtGui.QPushButton()
        self.Qt_reports.setItemWidget(Qreport, 2, Qbutton)
        Qreport.color = Qbutton
        Qbutton.clicked.connect(self.Qt_color_click)
        Qbutton.item = Qreport

        # annotate
        Qreport.reportid = reportid
        Qreport.callid = None

        Qreport.items = {None: Qreport}
        for callid, call in enumerate(report["calls"]):
            Qitem = QtGui.QTreeWidgetItem((call[0],))
            Qreport.addChild(Qitem)
            Qreport.items[callid] = Qitem

            # tooltip
            Qitem.setToolTip(0, str(call))

            # checkbox
            Qcheck = QtGui.QCheckBox()
            self.Qt_reports.setItemWidget(Qitem, 1, Qcheck)
            Qitem.checkbox = Qcheck
            Qcheck.stateChanged.connect(self.Qt_reportcheck_change)
            Qcheck.item = Qitem

            # colorbutton
            Qbutton = QtGui.QPushButton()
            self.Qt_reports.setItemWidget(Qitem, 2, Qbutton)
            Qitem.color = Qbutton
            Qbutton.clicked.connect(self.Qt_color_click)
            Qbutton.item = Qitem

            # annotate
            Qitem.reportid = reportid
            Qitem.callid = callid

        self.UI_report_update(reportid)
        self.Qt_columns_resize()

    def UI_report_update(self, reportid):
        report = self.reports[reportid]
        Qreport = self.Qt_Qreports[reportid]
        for callid, Qitem in Qreport.items.iteritems():
            Qitem.checkbox.setChecked(report["plotting"][callid])
            color = report["plotcolors"][callid]
            Qitem.color.setStyleSheet("background-color: %s;" % color)
            Qitem.color.setToolTip(color)

    def UI_reportinfo_set(self, infostr):
        self.Qt_reportinfo.setText(infostr)

    def UI_plot_show(self, metric, state=True):
        self.setting = True
        if metric not in self.Qt_Qplots:
            self.Qt_Qplots[metric] = self.plotfactory(self, metric)
        Qplot = self.Qt_Qplots[metric]
        if state:
            Qplot.plot_update()
            Qplot.show()
        else:
            Qplot.hide()
        self.setting = False

    def UI_metricinfo_set(self, infostr):
        self.Qt_metricinfo.setText(infostr)

    def UI_plots_update(self):
        for metric in self.Qt_Qplots:
            self.UI_plot_update(metric)

    def UI_plot_update(self, metric):
        if metric not in self.Qt_Qplots:
            return
        self.Qt_Qplots[metric].plot_update()

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
        if self.setting:
            return
        self.UI_report_select(item.reportid, item.callid)

    def Qt_reportcheck_change(self):
        if self.setting:
            return
        sender = self.sender()
        self.UI_reportcheck_change(sender.item.reportid, sender.item.callid,
                                   sender.isChecked())

    def Qt_color_click(self):
        sender = self.sender().item
        reportid = sender.reportid
        callid = sender.callid
        Qcolor = QtGui.QColor(self.reports[reportid]["plotcolors"][callid])
        Qcolor = QtGui.QColorDialog.getColor(Qcolor)
        if Qcolor.isValid():
            self.UI_reportcolor_change(reportid, callid, Qcolor.name())

    def Qt_metricselect_change(self):
        if self.setting:
            return
        self.UI_metricselect_change(str(self.Qt_metricslist.currentText()))

    def Qt_plot_clicked(self):
        self.UI_plot_clicked()
