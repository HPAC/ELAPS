#!/usr/bin/env python
"""GUI for Reports."""
from __future__ import division, print_function

import elaps.defines as defines
import elaps.io
import elaps.plot
from elaps.report import apply_stat

import sys
import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure

from reportitem import QReportItem


class Viewer(QtGui.QMainWindow):

    """GUI for Reports."""

    def __init__(self, *filenames, **kwargs):
        """Initialize the Viewer."""
        if "app" in kwargs:
            self.Qapp = kwargs["app"]
        else:
            self.Qapp = QtGui.QApplication(sys.argv)
            self.Qapp.playmat = None
        self.Qapp.viewer = self
        QtGui.QMainWindow.__init__(self)

        self.discard_firstrep = True
        self.stats_showing = ["med"]
        self.metric_showing = None
        self.colors = defines.colors[::-1]

        # load some stuff
        self.papi_names = elaps.io.load_papinames()
        self.metrics = elaps.io.load_all_metrics()

        # set up UI
        self.UI_init()
        if "reset" not in kwargs or not kwargs["reset"]:
            try:
                self.UI_settings_load()
            except:
                pass

        # load reports
        for filename in filenames:
            self.report_load(filename)

        if self.metric_showing not in self.metrics:
            self.metric_showing = "Gflops/s"

        self.UI_setall()

    def UI_init(self):
        """Initialize all GUI elements."""
        self.UI_setting = 1

        # window
        self.pyqtConfigure(
            windowTitle="ELAPS:Viewer",
            dockNestingEnabled=True,
            unifiedTitleAndToolBarOnMac=True
        )
        self.setTabPosition(QtCore.Qt.LeftDockWidgetArea,
                            QtGui.QTabWidget.North)
        center = QtGui.QWidget()
        self.setCentralWidget(center)
        center.hide()
        self.statusBar()

        def create_menus():
            """Create all menus."""
            menu = self.menuBar()

            # file
            fileM = menu.addMenu("File")

            # file > load
            fileM.addAction(QtGui.QAction(
                "Load Report ...", self,
                shortcut=QtGui.QKeySequence.Open,
                triggered=self.on_report_load
            ))

            # file
            fileM.addSeparator()

            fileM.addAction(QtGui.QAction(
                "Start PlayMat", self, triggered=self.on_playmat_start
            ))

        def create_toolbar():
            """Create all toolbars."""
            # open
            openT = self.addToolBar("Open")
            openT.pyqtConfigure(movable=False, objectName="Open")
            open_ = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton),
                "Open", self,
                triggered=self.on_report_load
            )
            openT.addAction(open_)

            # metric
            self.UI_metric = QtGui.QComboBox()
            self.UI_metric.currentIndexChanged[str].connect(
                self.on_metric_change
            )
            metricsT = self.addToolBar("Metrics")
            metricsT.pyqtConfigure(movable=False, objectName="Metrics")
            metricsT.addWidget(self.UI_metric)

            self.addToolBarBreak()

            # stats
            statsT = self.addToolBar("Statistics")
            statsT.pyqtConfigure(movable=False, objectName="Statistics")
            self.UI_stats = []
            for stat_name, desc in (
                ("min", "minimum"),
                ("med", "median"),
                ("max", "maximum"),
                ("avg", "average"),
                ("std", "standard deviation"),
                ("all", "all data points")
            ):
                stat = QtGui.QCheckBox(
                    stat_name, toolTip=desc, toggled=self.on_stat_toggle
                )
                stat.stat_name = stat_name
                statsT.addWidget(stat)
                self.UI_stats.append((stat_name, stat))

            # firstrep
            firstrepT = self.addToolBar("First Repetitions")
            firstrepT.pyqtConfigure(movable=False,
                                    objectName="First Repetitions")
            self.UI_discard_firstrep = QtGui.QCheckBox(
                "Ignore first repetitions",
                toggled=self.on_discard_firstrep_toggle
            )
            firstrepT.addWidget(self.UI_discard_firstrep)

        def create_reports():
            """Create the reports list."""
            self.UI_reports = QtGui.QTreeWidget(
                acceptDrops=True, minimumWidth=300,
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                dragDropMode=QtGui.QTreeWidget.InternalMove,
                currentItemChanged=self.on_report_select,
                itemExpanded=self.on_report_expand,
                itemCollapsed=self.on_report_collapse,
                customContextMenuRequested=self.on_reports_rightclick
            )
            self.UI_reports.model().rowsInserted.connect(
                self.on_reports_reorder
            )
            self.UI_reports.setHeaderLabels(("report", "", "color", "label"))
            self.UI_reports.reports = {}

            reportsD = QtGui.QDockWidget(
                "Reports",
                objectName="Reports",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            reportsD.setWidget(self.UI_reports)

            return reportsD

        def create_plot():
            """Create the plot."""
            self.UI_figure = Figure()
            self.UI_canvas = FigureCanvasQTAgg(self.UI_figure)

            # toolbar
            toolbar = NavigationToolbar2QT(self.UI_canvas, self)

            plotL = QtGui.QVBoxLayout(spacing=0)
            plotL.setContentsMargins(0, 0, 0, 0)
            plotL.addWidget(self.UI_canvas, 1)
            plotL.addWidget(toolbar)

            plotW = QtGui.QWidget()
            plotW.setLayout(plotL)

            plotD = QtGui.QDockWidget(
                "Plot", objectName="Plot",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            plotD.setWidget(plotW)

            return plotD

        def create_table():
            """Create the table."""
            self.UI_table = QtGui.QTableWidget()
            self.UI_table.setColumnCount(5)
            self.UI_table.setHorizontalHeaderLabels(
                ["min", "med", "max", "avg", "std"]
            )

            tableD = QtGui.QDockWidget(
                "Table", objectName="Table",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            tableD.setWidget(self.UI_table)

            return tableD

        def create_info():
            """Create info text box."""
            UI_info = QtGui.QLabel(
                alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop,
                sizePolicy=QtGui.QSizePolicy(
                    QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
                ),
                textInteractionFlags=QtCore.Qt.TextSelectableByMouse
            )
            UI_info.setContentsMargins(4, 4, 4, 4)

            self.UI_info = QtGui.QDockWidget(
                "Report Info", objectName="Report Info",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            self.UI_info.setWidget(UI_info)

            return self.UI_info

        create_menus()
        create_toolbar()
        reportsD = create_reports()
        plotD = create_plot()
        tableD = create_table()
        infoD = create_info()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, reportsD)
        self.splitDockWidget(reportsD, plotD, QtCore.Qt.Horizontal)
        self.splitDockWidget(reportsD, infoD, QtCore.Qt.Vertical)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tableD)
        self.tabifyDockWidget(plotD, tableD)
        infoD.hide()
        plotD.raise_()

        self.show()

        self.UI_setting -= 1

    def UI_settings_load(self):
        """Load Qt settings."""
        settings = QtCore.QSettings("HPAC", "ELAPS:Viewer")
        state = eval(str(settings.value("state", type=str)))
        self.stats_showing, self.metric_showing, self.discard_firstrep = state
        self.UI_setting += 1
        self.restoreGeometry(settings.value("geometry",
                                            type=QtCore.QByteArray))
        self.restoreState(settings.value("windowState",
                                         type=QtCore.QByteArray))
        self.UI_setting -= 1

    def start(self):
        """Start the Viewer(enter the main loop)."""
        import signal
        signal.signal(signal.SIGINT, self.on_console_quit)

        # make sure python handles signals every 500ms
        timer = QtCore.QTimer(timeout=lambda: None)
        timer.start(500)

        sys.exit(self.Qapp.exec_())

    # utility
    def log(self, *args):
        """Log a message to stdout and statusbar."""
        msg = " ".join(map(str, args))
        self.statusBar().showMessage(msg, 2000)
        print(msg)

    def alert(self, *args):
        """Log a message to stderr and statusbar."""
        msg = " ".join(map(str, args))
        self.statusBar().showMessage(msg)
        print("\033[31m%s\033[0m" % msg, file=sys.stderr)

    def UI_alert(self, *args, **kwargs):
        """Alert a messagebox."""
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    # report routines
    def report_load(self, filename, index=None, UI_alert=False):
        """Load a report."""
        filename = os.path.abspath(filename)

        # check if loaded
        if index is None:
            for UI_report in self.UI_reportitems():
                if UI_report.filename == filename:
                    self.report_reload(UI_report, UI_alert)
                    return

        # load report
        try:
            report = elaps.io.load_report(filename)
        except:
            if UI_alert:
                self.UI_alert("ERROR: Can't load %r" % filename)
            else:
                self.alert("ERROR: Can't load %r" % filename)
            return

        # add counters
        for counter_name in report.experiment.papi_counters:
            counter_info = self.papi_names[counter_name]
            metric_name = counter_info["short"]
            if metric_name in self.metrics:
                continue

            def metric(data, **kwargs):
                return data.get(counter_name)
            metric.name = metric_name
            metric.__doc__ = counter_info["long"]
            self.metrics[metric_name] = metric

        if index is None:
            self.log("Loaded %r" % filename)
            index = self.UI_reports.topLevelItemCount()

        self.UI_setting += 1
        UI_report = QReportItem(self, filename, report)
        self.UI_reports.insertTopLevelItem(index, UI_report)
        self.UI_reports.setCurrentItem(UI_report)
        self.UI_setting -= 1

        return UI_report

    def report_close(self, UI_report):
        """Close a report."""
        self.UI_setting += 1
        UI_report.close()
        self.UI_reports.takeTopLevelItem(
            self.UI_reports.indexOfTopLevelItem(UI_report)
        )
        self.UI_setting -= 1

    def report_reload(self, UI_report, UI_alert=False):
        """Reload a report."""
        showing = [
            UI_item.callid for UI_item in [UI_report] + UI_report.children
            if UI_item.showing
        ]
        index = self.UI_reports.indexOfTopLevelItem(UI_report)
        self.report_close(UI_report)
        UI_report = self.report_load(UI_report.filename, index, UI_alert)

        for UI_item in [UI_report] + UI_report.children:
            UI_item.showing = UI_item.callid in showing
        self.log("Reloaded %r" % UI_report.filename)

    # playmat
    def playmat_start(self, filename=None):
        """Start the PlayMat."""
        from playmat import PlayMat
        PlayMat(app=self.Qapp, load=filename)

    # UI utility
    def UI_reportitems(self):
        """Get all UI_reports."""
        return map(self.UI_reports.topLevelItem,
                   range(self.UI_reports.topLevelItemCount()))

    # UI setters
    def UI_setall(self):
        """Set all UI elements."""
        self.UI_metric_set()
        self.UI_stats_set()
        self.UI_discard_firstrep_set()
        self.UI_reports_set()
        self.UI_info_set()
        self.UI_plot_set()
        self.UI_table_set()

    def UI_metric_set(self):
        """Set UI element: metric."""
        self.UI_setting += 1
        if self.UI_metric.count() != len(self.metrics):
            self.UI_metric.clear()
            for i, metric_name in enumerate(sorted(self.metrics)):
                self.UI_metric.addItem(metric_name)
                self.UI_metric.setItemData(
                    i, self.metrics[metric_name].__doc__.strip(),
                    QtCore.Qt.ToolTipRole
                )
        self.UI_metric.setCurrentIndex(
            self.UI_metric.findText(self.metric_showing)
        )
        self.UI_setting -= 1

    def UI_stats_set(self):
        """Set UI element: stats."""
        self.UI_setting += 1
        for stat_name, stat in self.UI_stats:
            stat.setChecked(stat_name in self.stats_showing)
        self.UI_setting -= 1

    def UI_discard_firstrep_set(self):
        """Set UI element: discard_firstrep."""
        self.UI_setting += 1
        self.UI_discard_firstrep.setChecked(self.discard_firstrep)
        self.UI_setting -= 1

    def UI_reports_set(self):
        """Set UI element: reports."""
        self.UI_setting += 1
        for UI_reportitem in self.UI_reportitems():
            UI_reportitem.UI_setall()
        self.UI_reports_resizecolumns()
        self.UI_setting -= 1

    def UI_info_set(self):
        """Set UI element: info."""
        self.UI_setting += 1
        current = self.UI_reports.currentItem()
        if current:
            self.UI_info.setWindowTitle("Report %s" % current.reportname)
            self.UI_info.widget().setText(str(current.experiment))
        self.UI_info.setVisible(bool(current))
        self.UI_setting -= 1

    def UI_plot_set(self):
        """Set UI element: plot."""
        self.UI_setting += 1

        # get metric
        metric = self.metrics[self.metric_showing]

        # collect plot data
        plot_data = []
        colors = []
        range_vars = []
        for UI_report in self.UI_reportitems():
            UI_items = [UI_report] + UI_report.children
            if not any(UI_item.showing for UI_item in UI_items):
                continue
            report = UI_report.report
            ex = report.experiment
            if self.discard_firstrep:
                report = report.discard_first_repetitions()
            if ex.range and ex.range_var not in range_vars:
                range_vars.append(ex.range_var)
            for UI_item in UI_items:
                if UI_item.showing:
                    plot_data.append((
                        UI_item.plotlabel,
                        report.apply_metric(metric, UI_item.callid)
                    ))
                    colors.append(UI_item.color)

        xlabel = " = ".join(map(str, range_vars))
        elaps.plot.plot(plot_data, self.stats_showing, colors, {}, xlabel,
                        metric.name, {}, self.UI_figure)
        self.UI_canvas.draw()
        self.UI_setting -= 1

    def UI_table_set(self):
        """Set UI element: table."""
        self.UI_setting += 1
        current = self.UI_reports.currentItem()
        if current is None:
            self.UI_table.setRowCount(0)
            self.UI_setting -= 1
            return

        # compute data
        report = current.report
        if self.discard_firstrep:
            report = report.discard_first_repetitions()
        stat_names = ("min", "med", "max", "avg", "std")
        table_data = {}
        for metric_name, metric in self.metrics.items():
            metric_data = report.apply_metric(metric, current.callid)
            metric_values = [value for values in metric_data.values()
                             for value in values if value is not None]
            if not metric_values:
                continue
            table_data[metric_name] = dict(
                (stat_name, apply_stat(stat_name, metric_values))
                for stat_name in stat_names
            )

        # display data
        self.UI_table.setRowCount(len(table_data))
        self.UI_table.setVerticalHeaderLabels(sorted(table_data))
        for i, metric_name in enumerate(sorted(table_data)):
            for j, stat_name in enumerate(stat_names):
                self.UI_table.setItem(i, j, QtGui.QTableWidgetItem(
                    str(table_data[metric_name][stat_name])
                ))

        self.UI_setting -= 1

    def UI_reports_resizecolumns(self):
        """Resize the columns in the report list."""
        totalwidth = 0
        for colid in range(self.UI_reports.columnCount()):
            self.UI_reports.resizeColumnToContents(colid)
            totalwidth += self.UI_reports.columnWidth(colid)

    # UI events:
    def on_console_quit(self, *args):
        """Event: Ctrl-C from the console."""
        print("\r", end="")
        self.close()
        if self.Qapp.playmat:
            self.Qapp.playmat.close()
        self.Qapp.quit()

    def closeEvent(self, event):
        """Event: close main window."""
        settings = QtCore.QSettings("HPAC", "ELAPS:Viewer")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        state = self.stats_showing, self.metric_showing, self.discard_firstrep
        settings.setValue("state", repr(state))

    @pyqtSlot()
    def on_playmat_start(self):
        """Event: start PlayMat."""
        if not self.Qapp.playmat:
            self.playmat_start()
            return
        self.Qapp.playmat.show()
        self.Qapp.playmat.raise_()

    @pyqtSlot(str)
    def on_metric_change(self, value):
        """Event: metric changed."""
        if self.UI_setting:
            return
        self.metric_showing = str(value)
        self.UI_plot_set()

    @pyqtSlot(bool)
    def on_stat_toggle(self, checked):
        """Event: stat toggled."""
        if self.UI_setting:
            return
        self.stats_showing = [stat_name for stat_name, stat in self.UI_stats
                              if stat.isChecked()]
        self.UI_plot_set()
        self.UI_table_set()

    @pyqtSlot(bool)
    def on_discard_firstrep_toggle(self, checked):
        """Event: discard_firstrep toggled."""
        if self.UI_setting:
            return
        self.discard_firstrep = checked
        self.UI_plot_set()
        self.UI_table_set()

    @pyqtSlot(QtCore.QPoint)
    def on_reports_rightclick(self, pos):
        """Event: right click on reports."""
        globalpos = self.UI_reports.viewport().mapToGlobal(pos)

        # context menu
        menu = QtGui.QMenu()

        if self.UI_reports.currentItem():
            # report selected
            menu.addAction(QtGui.QAction(
                "Reload", self, triggered=self.on_report_reload
            ))
            menu.addAction(QtGui.QAction(
                "Close", self, triggered=self.on_report_close
            ))
            menu.addAction(QtGui.QAction(
                "Open in PlayMat", self, triggered=self.on_report_playmat_open
            ))
            menu.addSeparator()
        else:
            # no report selected
            menu.addAction(QtGui.QAction(
                "Open", self, triggered=self.on_report_load
            ))

        if self.UI_reportitems():
            # reports loaded
            menu.addAction(QtGui.QAction(
                "Reload all", self, triggered=self.on_report_reload_all
            ))
            menu.addAction(QtGui.QAction(
                "Close all", self, triggered=self.on_report_close_all
            ))

        menu.exec_(globalpos)

    @pyqtSlot()
    def on_report_load(self):
        """Event: load Report."""
        filenames = QtGui.QFileDialog.getOpenFileNames(
            self, "Load Experiment", elaps.io.reportpath,
            " ".join("*." + ext for ext in defines.report_extensions)
        )
        if not filenames:
            return
        for filename in filenames:
            self.report_load(str(filename))
        self.UI_setall()

    @pyqtSlot()
    def on_report_reload(self):
        """Event: reload Report."""
        UI_item = self.UI_reports.currentItem()
        if UI_item.parent():
            UI_item = UI_item.parent()
        self.report_reload(UI_item)
        self.UI_setall()

    @pyqtSlot()
    def on_report_reload_all(self):
        """Event: reload all Reports."""
        for UI_report in self.UI_reportitems():
            self.report_reload(UI_report)
        self.UI_setall()

    @pyqtSlot()
    def on_report_close(self):
        """Event: close Report."""
        UI_item = self.UI_reports.currentItem()
        if UI_item.parent():
            UI_item = UI_item.parent()
        self.report_close(UI_item)
        self.UI_setall()

    @pyqtSlot()
    def on_report_close_all(self):
        """Event: close all Reports."""
        for UI_report in reversed(self.UI_reportitems()):
            self.report_close(UI_report)
        self.UI_setall()

    @pyqtSlot()
    def on_report_playmat_open(self):
        """Event: open Report in PlayMat."""
        UI_item = self.UI_reports.currentItem()
        filename = UI_item.filename
        if not self.Qapp.playmat:
            self.playmat_start(filename)
            return
        self.Qapp.playmat.experiment_load(filename)
        self.Qapp.playmat.UI_setall()
        self.Qapp.playmat.show()
        self.Qapp.playmat.raise_()

    @pyqtSlot()
    def on_reports_reorder(self):
        """Event: reordered Reports."""
        if self.UI_setting:
            return
        self.UI_reports_set()
        self.UI_plot_set()

    @pyqtSlot()
    def on_report_select(self):
        """Event: select Report."""
        self.UI_info_set()
        self.UI_table_set()

    @pyqtSlot(QtGui.QTreeWidgetItem)
    def on_report_expand(self, item):
        """Event: expand Report."""
        self.UI_reports_resizecolumns()

    @pyqtSlot(QtGui.QTreeWidgetItem)
    def on_report_collapse(self, item):
        """Event: collapse Report."""
        self.UI_reports_resizecolumns()
