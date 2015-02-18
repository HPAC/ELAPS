#!/usr/bin/env python
from __future__ import division, print_function

from viewer import Viewer

import sys
from copy import deepcopy

from PyQt4 import QtCore, QtGui


class QViewer(Viewer):
    def __init__(self, plotfactory, app=None, loadstate=True):
        if app:
            self.Qt_app = app
        else:
            self.Qt_app = QtGui.QApplication(sys.argv)
            self.Qt_app.gui = None
        self.Qt_app.viewer = self
        self.plotfactory = plotfactory
        self.Qt_setting = 0
        Viewer.__init__(self, loadstate)

    def state_init(self, load=True):
        if load:
            settings = QtCore.QSettings("HPAC", "ELAPS:Viewer")
            self.Qt_setting += 1
            self.Qt_window.restoreGeometry(
                settings.value("geometry").toByteArray()
            )
            self.Qt_window.restoreState(
                settings.value("windowState").toByteArray()
            )
            self.Qt_setting -= 1
            try:
                self.state = eval(str(settings.value("appState").toString()))
            except:
                self.state_reset()
        else:
            self.state_reset()

    def UI_init(self):
        self.UI_hasHTML = True
        # window
        self.Qt_window = QtGui.QMainWindow()
        window = self.Qt_window
        window.setWindowTitle("Viewer")
        window.setUnifiedTitleAndToolBarOnMac(True)
        window.closeEvent = self.Qt_window_close
        window.setDockNestingEnabled(True)
        window.setTabPosition(QtCore.Qt.LeftDockWidgetArea,
                              QtGui.QTabWidget.North)

        center = QtGui.QWidget()
        window.setCentralWidget(center)
        center.hide()

        def create_menus():
            menu = window.menuBar()

            # file
            fileM = menu.addMenu("File")

            # file > load
            load = QtGui.QAction("Open Report", window)
            fileM.addAction(load)
            load.setShortcut(QtGui.QKeySequence.Open)
            load.triggered.connect(self.Qt_report_load_click)

            # file
            fileM.addSeparator()

            # gui
            gui = QtGui.QAction("Start Sampler", window)
            fileM.addAction(gui)
            gui.triggered.connect(self.Qt_sampler_start_click)

            # plot
            plotM = menu.addMenu("Plot")

            # duplicate
            duplicate = QtGui.QAction("Duplicate", window)
            plotM.addAction(duplicate)
            duplicate.triggered.connect(self.Qt_plot_duplicate)

            # export raw data
            export = QtGui.QAction("Export Data", window)
            plotM.addAction(export)
            export.triggered.connect(self.Qt_plot_duplicate)

        def create_toolbars():
            # load
            reportsT = window.addToolBar("Reports")
            reportsT.setObjectName("ReportsToolbar")
            load = QtGui.QAction(self.Qt_app.style().standardIcon(
                QtGui.QStyle.SP_DialogOpenButton
            ), "Open", window)
            reportsT.addAction(load)
            load.triggered.connect(self.Qt_report_load_click)

            # metric
            metricsT = window.addToolBar("Metrics")
            metricsT.setObjectName("Metrics")
            self.Qt_metric = QtGui.QComboBox()
            metricsT.addWidget(self.Qt_metric)
            self.Qt_metric.currentIndexChanged.connect(self.Qt_metric_change)
            window.addToolBarBreak()

            # statistics
            self.Qt_Qstats = {}
            statsT = window.addToolBar("Statistics")
            statsT.setObjectName("Statistics")
            for statname, desc in self.stats_desc:
                stat = QtGui.QCheckBox(statname)
                statsT.addWidget(stat)
                stat.statname = statname
                stat.stateChanged.connect(self.Qt_stat_change)
                stat.setToolTip(desc)
                self.Qt_Qstats[statname] = stat

        def create_reports():
            reportsD = QtGui.QDockWidget("Reports")
            reportsD.setObjectName("Reports")
            reportsD.setFeatures(
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable
            )
            self.Qt_reports = QtGui.QTreeWidget()
            reportsD.setWidget(self.Qt_reports)
            self.Qt_reports.setHeaderLabels(
                ("report", "", "color", "system", "#t", "blas")
            )
            self.Qt_columns_resize()
            self.Qt_reports.currentItemChanged.connect(self.Qt_report_select)
            self.Qt_reports.itemExpanded.connect(self.Qt_report_expanded)

            return reportsD

        def create_center():
            tabs = QtGui.QTabWidget()
            window.setCentralWidget(tabs)

            # window > right > tabs > plot
            self.Qt_plot = self.plotfactory()
            tabs.addTab(self.Qt_plot, "Plot")

            # window > right > tabs > table
            self.Qt_data = QtGui.QTableWidget()
            tabs.addTab(self.Qt_data, "data")
            self.Qt_data.setColumnCount(5)
            self.Qt_data.setHorizontalHeaderLabels(
                ["med", "min", "avg", "max", "std"]
            )

        def create_plot():
            plotD = QtGui.QDockWidget("Plot")
            plotD.setObjectName("Plot")
            plotD.setFeatures(
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable
            )
            self.Qt_plot = self.plotfactory()
            plotD.setWidget(self.Qt_plot)

            return plotD

        def create_table():
            tableD = QtGui.QDockWidget("Table")
            tableD.setObjectName("Table")
            tableD.setFeatures(
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable
            )
            self.Qt_data = QtGui.QTableWidget()
            tableD.setWidget(self.Qt_data)
            self.Qt_data.setColumnCount(5)
            self.Qt_data.setHorizontalHeaderLabels(
                ["med", "min", "avg", "max", "std"]
            )

            return tableD

        def create_info():
            infoD = QtGui.QDockWidget("Report Info")
            infoD.setObjectName("Report Info")
            infoD.setFeatures(
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable
            )

            # info
            self.Qt_reportinfo = QtGui.QLabel()
            infoD.setWidget(self.Qt_reportinfo)
            self.Qt_reportinfo.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse
            )

            return infoD

        create_menus()
        create_toolbars()
        reportsD = create_reports()
        window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, reportsD)
        plotD = create_plot()
        window.splitDockWidget(reportsD, plotD, QtCore.Qt.Horizontal)
        infoD = create_info()
        window.splitDockWidget(plotD, infoD, QtCore.Qt.Vertical)
        tableD = create_table()
        window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tableD)
        window.tabifyDockWidget(plotD, tableD)
        plotD.raise_()

        # window > left > metrics > info
        self.Qt_metricinfo = QtGui.QLabel()

        self.Qt_window.show()

        # Qt objects
        self.Qt_Qreports = []

    def UI_start(self):
        sys.exit(self.Qt_app.exec_())

    def UI_alert(self, *args, **kwargs):
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def Qt_columns_resize(self):
        for colid in range(self.Qt_reports.columnCount()):
            self.Qt_reports.resizeColumnToContents(colid)

    # setters
    def UI_metrics_update(self):
        self.Qt_setting += 1
        self.Qt_metric.clear()
        for i, name in enumerate(sorted(self.metrics)):
            self.Qt_metric.addItem(self.metricnames[name],
                                   QtCore.QVariant(name))
            self.Qt_metric.setItemData(
                i, self.metrics[name].__doc__.strip(), QtCore.Qt.ToolTipRole
            )
        self.Qt_setting -= 1
        self.Qt_metric.setCurrentIndex(
            self.Qt_metric.findData(QtCore.QVariant(self.metric_selected))
        )

    def UI_metric_set(self):
        self.Qt_metric.setCurrentIndex(
            self.Qt_metric.findData(QtCore.QVariant(self.metric_selected))
        )

    def UI_stats_set(self):
        for stat, Qstat in self.Qt_Qstats.iteritems():
            Qstat.setChecked(stat in self.stats_showing)

    def UI_report_add(self, reportid=None):
        if reportid is None:
            reportid = len(self.reports) - 1
        report = self.reports[reportid]
        sampler = report["sampler"]

        #  tree item
        ntstr = str(report["nt"])
        if report["userange"]["outer"] == "threads":
            ntstr = str(report["ranges"]["threads"])
        Qreport = QtGui.QTreeWidgetItem((
            report["name"],
            "",
            "",
            sampler["system_name"],
            ntstr,
            sampler["blas_name"],
        ))
        self.Qt_reports.addTopLevelItem(Qreport)
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
        for callid in report["plotcolors"]:
            if callid is None:
                continue
            call = report["calls"][callid]
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

        self.Qt_Qreports.append(Qreport)
        self.UI_report_update(reportid)
        self.Qt_columns_resize()
        self.Qt_reports.setCurrentItem(Qreport)

    def UI_report_update(self, reportid):
        report = self.reports[reportid]
        Qreport = self.Qt_Qreports[reportid]
        for callid, Qitem in Qreport.items.iteritems():
            Qitem.checkbox.setChecked((reportid, callid) in self.plots_showing)
            color = report["plotcolors"][callid]
            Qitem.color.setStyleSheet("background-color: %s;" % color)
            Qitem.color.setToolTip(color)

    def UI_metricinfo_set(self, infostr):
        self.Qt_metricinfo.setText(infostr)

    def UI_reportinfo_update(self):
        infostr = self.report_infostr_HTML()
        self.Qt_reportinfo.setText(infostr)

        self.Qt_data.setRowCount(len(self.metrics))
        names = [self.metricnames[metric] for metric in sorted(self.metrics)]
        self.Qt_data.setVerticalHeaderLabels(names)
        for i, metricname in enumerate(sorted(self.metrics)):
            data = self.get_metricdata(self.reportid_selected,
                                       self.callid_selected, metricname)
            if data is not None:
                data = list(sum((values for key, values in data), ()))
                for j, stat in enumerate(("med", "min", "avg", "max", "std")):
                    self.Qt_data.setItem(i, j, QtGui.QTableWidgetItem(
                        str(self.stat_funs[stat](data))
                    ))
            else:
                for j in range(5):
                    self.Qt_data.setItem(i, j, QtGui.QTableWidgetItem("NA"))

    def UI_plot_update(self):
        self.Qt_plot.plot(
            xlabel=self.plotrangevar,
            ylabel=self.metricnames[self.metric_selected],
            data=self.plotdata,
            colors=self.plotcolors
        )

    # event handlers
    def Qt_window_close(self, event):
        settings = QtCore.QSettings("HPAC", "Viewer")
        settings.setValue("geometry", self.Qt_window.saveGeometry())
        settings.setValue("windowState", self.Qt_window.saveState())
        settings.setValue("appState",
                          QtCore.QVariant(repr(self.state)))

    def Qt_sampler_start_click(self):
        self.UI_sampler_start()

    def Qt_report_load_click(self):
        filenames = QtGui.QFileDialog.getOpenFileNames(
            self.Qt_window,
            "Open Report(s)",
            self.reportpath,
            "*.smpl"
        )
        for filename in filenames:
            filename = str(filename)
            print(filename)
            if filename:
                self.UI_report_load(filename)

    def Qt_report_expanded(self, item):
        self.Qt_reports.resizeColumnToContents(0)

    def Qt_report_select(self, item):
        if self.Qt_setting:
            return
        self.UI_report_select(item.reportid, item.callid)

    def Qt_reportcheck_change(self):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        self.UI_reportcheck_change(sender.item.reportid, sender.item.callid,
                                   sender.isChecked())

    def Qt_color_click(self):
        sender = self.Qt_app.sender().item
        reportid = sender.reportid
        callid = sender.callid
        Qcolor = QtGui.QColor(self.reports[reportid]["plotcolors"][callid])
        Qcolor = QtGui.QColorDialog.getColor(Qcolor)
        if Qcolor.isValid():
            self.UI_reportcolor_change(reportid, callid, str(Qcolor.name()))

    def Qt_metric_change(self):
        if self.Qt_setting:
            return
        self.UI_metric_change(str(self.Qt_metric.itemData(
            self.Qt_metric.currentIndex()
        ).toString()))

    def Qt_stat_change(self):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        self.UI_stat_change(sender.statname, sender.isChecked())

    def Qt_plot_export(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            None,
            "Export plot data",
            self.reportpath,
            "*.dat"
        )
        filename = str(filename)
        if filename:
            self.UI_export(filename)

    def Qt_plot_duplicate(self):
        # TODO: DockWidget
        plot = self.plotfactory()
        plot.plot(
            xlabel=self.plotrangevar,
            ylabel=self.metricnames[self.metric_selected],
            data=deepcopy(self.plotdata),
            colors=deepcopy(self.plotcolors)
        )
        plot.show()
