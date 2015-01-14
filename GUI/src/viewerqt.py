#!/usr/bin/env python
from __future__ import division, print_function

from viewer import Viewer

import sys

from PyQt4 import QtCore, QtGui
import matplotlib.backends.backend_qt4agg as QtMPL
import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines


class Viewer_Qt(Viewer, QtGui.QApplication):
    def __init__(self):
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
        self.Qt_reports.setHeaderLabels(("report", "", "color", "sytem", "#t",
                                         "blas", "range"))
        self.Qt_columns_resize()
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

        # showplots
        self.Qt_showplots = QtGui.QGroupBox("plots")
        rightL.addWidget(self.Qt_showplots)
        showplotsL = QtGui.QVBoxLayout()
        self.Qt_showplots.setLayout(showplotsL)
        self.Qt_Qshowplots = []

        # plotting
        do = QtGui.QPushButton("do something")
        rightL.addWidget(do)
        do.clicked.connect(self.Qt_dosomething)

        # window
        self.Qt_window.show()

        # Qt objects
        self.Qt_Qreports = {}
        self.Qt_plots = {}

        # plot styles
        self.MPL_plotstyles = {
            "legend": {"linestyle": "-"},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":"},
            "avg": {"linestyle": "-."},
            "all": {"linestyle": "None", "marker": "."},
            "minmax": {"alpha": .25},
        }

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

    def UI_info_set(self, infostr):
        self.Qt_info.setText(infostr)

    def UI_showplots_update(self):
        self.setting = True
        for box in self.Qt_Qshowplots:
            box.deleteLater()
        self.Qt_Qshowplots = []
        QplotsL = self.Qt_showplots.layout()
        for metricname in self.metrics:
            Qbox = QtGui.QGroupBox(metricname)
            QplotsL.addWidget(Qbox)
            Qlayout = QtGui.QHBoxLayout()
            Qbox.setLayout(Qlayout)
            for plottypename in self.plottypenames:
                Qcheckbox = QtGui.QCheckBox(plottypename)
                Qlayout.addWidget(Qcheckbox)
                Qcheckbox.setChecked(self.showplots[metricname][plottypename])
                Qcheckbox.metric = metricname
                Qcheckbox.plottype = plottypename
                Qcheckbox.stateChanged.connect(self.Qt_showplots_change)
            self.Qt_Qshowplots.append(Qbox)
        self.setting = False

    def UI_plots_update(self):
        for metricname in self.showplots:
            self.UI_plot_update(metricname)

    def UI_plot_update(self, metricname):
        if not any(self.showplots[metricname].values()):
            if metricname in self.Qt_plots:
                self.Qt_plots[metricname].hide()
            return
        if metricname in self.Qt_plots:
            Qplot = self.Qt_plots[metricname]
            if Qplot.isHidden():
                Qplot.show()
        else:
            Qplot = QtGui.QDialog()
            Qplot.setWindowTitle(metricname)
            layout = QtGui.QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            Qplot.setLayout(layout)
            fig = MPLfig.Figure()
            Qcanvas = QtMPL.FigureCanvasQTAgg(fig)
            layout.addWidget(Qcanvas, 1)
            Qtoolbar = QtMPL.NavigationToolbar2QT(Qcanvas, Qplot)
            layout.addWidget(Qtoolbar)
            Qplot.axes = fig.add_subplot(111)
            Qplot.metricname = metricname
            Qplot.MPLfig = fig
            Qplot.Qcanvas = Qcanvas
            Qplot.show()

            self.Qt_plots[metricname] = Qplot

        fig = Qplot.MPLfig
        canvas = Qplot.Qcanvas
        axes = Qplot.axes
        showplots = self.showplots[metricname]

        # get the data
        plotdata = {}
        rangevarnames = set()
        for reportid, report in enumerate(self.reports):
            rangevarnames.add(report["rangevar"])
            for callid, state in report["plotting"].iteritems():
                if not report["plotting"][callid]:
                    continue
                rawdata = self.generateplotdata(reportid, callid, metricname)
                if not rawdata:
                    continue
                linedatas = {
                    plottype: [(x, self.plottypes[plottype](y))
                               for x, y in rawdata
                               if y is not None]
                    for plottype in showplots if showplots[plottype]
                }
                if "all" in linedatas:
                    linedatas["all"] = [(x, y) for x, ys in linedatas["all"]
                                        for y in ys]
                if "min" in linedatas and "max" in linedatas:
                    linedatas["minmax"] = [
                        p1 + (p2[1],) for p1, p2 in zip(linedatas["min"],
                                                        linedatas["max"])
                    ]
                    del linedatas["min"]
                    del linedatas["max"]
                plotdata[reportid, callid] = linedatas

        rangevarname = " = ".join(rangevarnames)

        # set up figure
        axes.cla()
        axes.set_xlabel(rangevarname)
        axes.set_ylabel(metricname)
        axes.hold(True)

        # add plots
        legend = []
        for (reportid, callid), linedatas in plotdata.iteritems():
            report = self.reports[reportid]
            color = report["plotcolors"][callid]
            legendlabel = report["name"]
            if callid is not None:
                legendlabel += " (%s)" % str(report["calls"][callid][0])
            legend.append((MPLlines.Line2D([], [], color=color,
                                           **self.MPL_plotstyles["legend"]),
                           legendlabel))
            for plottype, linedata in linedatas.iteritems():
                if plottype == "minmax":
                    x, y1, y2 = zip(*linedata)
                    axes.fill_between(x, y1, y2, color=color,
                                      **self.MPL_plotstyles[plottype])
                else:
                    x, y = zip(*linedata)
                    axes.plot(x, y, color=color,
                              **self.MPL_plotstyles[plottype])
        artists, labels = zip(*legend)
        axes.legend(artists, labels)
        canvas.draw()

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

    def Qt_showplots_change(self):
        if self.setting:
            return
        sender = self.sender()
        self.UI_showplots_change(sender.metric, sender.plottype,
                                 sender.isChecked())

    def Qt_plot_close(self, event):
        sender = self.sender()
        del self.Qt_plots[sender.metricname]

    def Qt_dosomething(self):
        self.UI_dosomething()


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Viewer_Qt()


if __name__ == "__main__":
    main()
