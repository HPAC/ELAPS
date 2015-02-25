#!/usr/bin/env python
"""Qt implementaiton of ELAPS:Viewer."""
from __future__ import division, print_function

from viewer import Viewer

import sys
from copy import deepcopy

from PyQt4 import QtCore, QtGui


class QViewer(Viewer):

    """ELAPS:Viewer implementation in Qt."""

    def __init__(self, plotfactory, app=None, loadstate=True):
        """Initialize the ELAPS:Viewer."""
        if app:
            self.Qt_app = app
        else:
            self.Qt_app = QtGui.QApplication(sys.argv)
            self.Qt_app.mat = None
        self.Qt_app.viewer = self
        self.plotfactory = plotfactory
        self.Qt_setting = 0
        self.Qt_initialized = False
        Viewer.__init__(self, loadstate)

    def state_init(self, load=True):
        """Try to load the state and geometry."""
        if not load:
            Viewer.state_init(self)
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
            self.log("Loaded previous state")
        except:
            Viewer.state_init(self)

    def UI_init(self):
        """Initialize all GUI elements."""
        self.Qt_setting += 1

        # window
        self.Qt_window = QtGui.QMainWindow()
        window = self.Qt_window
        window.setWindowTitle("ELAPS:Viewer")
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

            # drop files
            self.Qt_reports.setAcceptDrops(True)
            self.Qt_reports.dragEnterEvent = self.Qt_reports_dragenter
            self.Qt_reports.dragMoveEvent = self.Qt_reports_dragmove
            self.Qt_reports.dropEvent = self.Qt_reports_drop

            # context menu
            self.Qt_reports.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.Qt_reports.customContextMenuRequested.connect(
                self.Qt_report_contextmenu_show
            )
            self.Qt_report_contextmenu = QtGui.QMenu()

            # context menu > reload
            reload_ = QtGui.QAction("Reload", window)
            self.Qt_report_contextmenu.addAction(reload_)
            reload_.triggered.connect(self.Qt_report_reload)

            # context menu > close
            close = QtGui.QAction("Close", window)
            self.Qt_report_contextmenu.addAction(close)
            close.triggered.connect(self.Qt_report_close)

            self.Qt_report_contextmenu.reportid = None

            self.Qt_Qreports = {}

            return reportsD

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

        def create_statusbar():
            """Create the staus bar."""
            self.Qt_statusbar = window.statusBar()

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
        create_statusbar()

        window.show()

        self.Qt_setting -= 1
        self.Qt_initialized = True

    def UI_start(self):
        """Start the Viewer (main loop)."""
        import signal
        signal.signal(signal.SIGINT, self.Qt_console_quit)

        # make sure python handles signals every 500ms
        timer = QtCore.QTimer()
        timer.start(500)
        timer.timeout.connect(lambda: None)

        sys.exit(self.Qt_app.exec_())

    # utility
    def log(self, *args):
        """Also log messages to status for 2 sec."""
        self.UI_setstatus(" ".join(map(str, args)), 2000)
        Viewer.log(*args)

    def alert(self, *args):
        """Also log alert messages to status."""
        self.UI_setstatus(" ".join(map(str, args)))
        Viewer.alert(*args)

    def UI_alert(self, *args, **kwargs):
        """Show an alert message to the user."""
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_setstatus(self, msg, timeout=0):
        """Set the status message."""
        if self.Qt_initialized:
            self.Qt_statusbar.showMessage(msg, timeout)

    # resize
    def Qt_columns_resize(self):
        """Resize the columns in the reports list."""
        for colid in range(self.Qt_reports.columnCount()):
            self.Qt_reports.resizeColumnToContents(colid)

    # setters
    def UI_metrics_update(self):
        """Update the list of metrics."""
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
        """Set which metric is selected."""
        self.Qt_metric.setCurrentIndex(
            self.Qt_metric.findData(QtCore.QVariant(self.metric_selected))
        )

    def UI_stats_set(self):
        """Set which statistics are selected."""
        for stat, Qstat in self.Qt_Qstats.iteritems():
            Qstat.setChecked(stat in self.stats_showing)

    def UI_report_add(self, reportid):
        """Add a report to the list."""
        if reportid in self.Qt_Qreports:
            # report was reloaded
            self.UI_report_remove(reportid)

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
        for callid in sorted(report["plotcolors"]):
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

        self.Qt_Qreports[reportid] = Qreport
        self.UI_report_update(reportid)
        self.Qt_columns_resize()
        self.Qt_reports.setCurrentItem(Qreport)

    def UI_report_remove(self, reportid):
        """Remove a report from the list."""
        self.Qt_reports.takeTopLevelItem(
            self.Qt_reports.indexOfTopLevelItem(self.Qt_Qreports[reportid])
        )
        del self.Qt_Qreports[reportid]

    def UI_report_update(self, reportid):
        """Update a listed report."""
        report = self.reports[reportid]
        Qreport = self.Qt_Qreports[reportid]
        for callid, Qitem in Qreport.items.iteritems():
            Qitem.checkbox.setChecked((reportid, callid) in self.plots_showing)
            color = report["plotcolors"][callid]
            Qitem.color.setStyleSheet("background-color: %s;" % color)
            Qitem.color.setToolTip(color)

    def UI_reportinfo_update(self):
        """Upate the report info and table."""
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

    def UI_reportinfo_clear(self):
        """Clear the report info and table."""
        self.Qt_reportinfo.setText("")
        for i in range(len(self.metrics)):
            for j in range(5):
                self.Qt_data.setItem(i, j, QtGui.QTableWidgetItem(""))

    def UI_plot_update(self):
        """Update the plot."""
        self.Qt_plot.plot(
            xlabel=self.plotrangevar,
            ylabel=self.metricnames[self.metric_selected],
            data=self.plotdata,
            colors=self.plotcolors
        )

    def UI_sampler_start(self):
        """Start the Mat."""
        from qt_mat import QMat
        QMat(self.Qt_app)

    # event handlers
    def Qt_console_quit(self, *args):
        """Event: Ctrl-C from the console."""
        print("\r", end="")
        self.Qt_window.close()
        if self.Qt_app.mat:
            self.Qt_app.mat.Qt_window.close()
        self.Qt_app.quit()

    def Qt_window_close(self, event):
        """Event: Main window closed."""
        settings = QtCore.QSettings("HPAC", "Viewer")
        settings.setValue("geometry", self.Qt_window.saveGeometry())
        settings.setValue("windowState", self.Qt_window.saveState())
        settings.setValue("appState",
                          QtCore.QVariant(repr(self.state)))

    def Qt_sampler_start_click(self):
        """Event: Start ELAPS:Sampler."""
        self.UI_sampler_start()

    def Qt_report_load_click(self):
        """Event: Load a report."""
        filenames = QtGui.QFileDialog.getOpenFileNames(
            self.Qt_window,
            "Open Report(s)",
            self.reportpath,
            "*.emr"
        )
        for filename in filenames:
            filename = str(filename)
            if filename:
                self.UI_report_load(filename)

    def Qt_report_expanded(self, item):
        """Event: Expand a report."""
        self.Qt_reports.resizeColumnToContents(0)

    def Qt_report_select(self, item):
        """Event: Report (un)selected."""
        if self.Qt_setting:
            return
        if item:
            self.UI_report_select(item.reportid, item.callid)
        else:
            self.UI_report_select(None, None)

    def Qt_reports_dragenter(self, Qevent):
        """Event: Dragging into report list."""
        for url in Qevent.mimeData().urls():
            if str(url.toLocalFile())[-4:] == ".emr":
                Qevent.acceptProposedAction()
                return

    def Qt_reports_dragmove(self, Qevent):
        """Event: Dragging in report list."""
        self.Qt_reports_dragenter(Qevent)

    def Qt_reports_drop(self, Qevent):
        """Event: Files dropped in report list."""
        for url in Qevent.mimeData().urls():
            filename = str(url.toLocalFile())
            if filename[-4:] == ".emr":
                self.UI_report_load(filename)

    def Qt_report_contextmenu_show(self, pos):
        """Event: Report context menu (right click)."""
        item = self.Qt_reports.itemAt(pos)
        if not item:
            return
        pos = self.Qt_reports.viewport().mapToGlobal(pos)
        self.Qt_report_contextmenu.reportid = item.reportid
        self.Qt_report_contextmenu.exec_(pos)

    def Qt_report_reload(self):
        """Event: Reload a report."""
        self.UI_report_reload(self.Qt_report_contextmenu.reportid)

    def Qt_report_close(self):
        """Event: close a report."""
        self.UI_report_close(self.Qt_report_contextmenu.reportid)

    def Qt_reportcheck_change(self):
        """Event: Selected to show/hide a report (or call) from the plot."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        self.UI_reportcheck_change(sender.item.reportid, sender.item.callid,
                                   sender.isChecked())

    def Qt_color_click(self):
        """Event: Clicked the color selection panel."""
        sender = self.Qt_app.sender().item
        reportid = sender.reportid
        callid = sender.callid
        Qcolor = QtGui.QColor(self.reports[reportid]["plotcolors"][callid])
        Qcolor = QtGui.QColorDialog.getColor(Qcolor)
        if Qcolor.isValid():
            self.UI_reportcolor_change(reportid, callid, str(Qcolor.name()))

    def Qt_metric_change(self):
        """Event: Changed which metric to show."""
        if self.Qt_setting:
            return
        self.UI_metric_change(str(self.Qt_metric.itemData(
            self.Qt_metric.currentIndex()
        ).toString()))

    def Qt_stat_change(self):
        """Event: Changed which statistics to show."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        self.UI_stat_change(sender.statname, sender.isChecked())

    def Qt_plot_export(self):
        """Event: Export the plot's raw data."""
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
        """Event: Duplicate the plot."""
        # TODO: DockWidget
        plot = self.plotfactory()
        plot.plot(
            xlabel=self.plotrangevar,
            ylabel=self.metricnames[self.metric_selected],
            data=deepcopy(self.plotdata),
            colors=deepcopy(self.plotcolors)
        )
        plot.show()
