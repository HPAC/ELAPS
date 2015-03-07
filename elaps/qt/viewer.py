#!/usr/bin/env python
"""GUI for Reports."""
from __future__ import division, print_function

import elaps.io
import elaps.plot

import sys
import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from matplotlib.backends.backend_qt4agg import (FigureCanvas,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure


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

        self.stats_showing = ["med"]
        self.metric_showing = ["Gflops/s"]
        self.reports = {}
        self.report_colors = {}
        self.reports_showing = set()
        self.reportitem_selected = (None, None)
        self.colorpool = elaps.plot.default_colors[::-1]

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

        def create_reports():
            """Create the reports list."""
            self.UI_reports = QtGui.QTreeWidget(
                acceptDrops=True,
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                currentItemChanged=self.on_report_select,
                itemExpanded=self.on_report_expand,
                itemCollapsed=self.on_report_collapse,
                customContextMenuRequested=self.on_report_contextmenu_show
            )
            self.UI_reports.dragEnterEvent = self.on_reports_dragenter
            self.UI_reports.dragMoveEvent = self.on_reports_dragmove
            self.UI_reports.dropEvent = self.on_reports_drop
            self.UI_reports.setFixedWidth(300)
            self.UI_reports.setHeaderLabels(
                ("report", "", "color", "system", "blas")
            )
            self.UI_reports.reports = {}

            reportsD = QtGui.QDockWidget(
                "Reports",
                objectName="Reports",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            reportsD.setWidget(self.UI_reports)

            # context menu
            self.UI_report_contextmenu = QtGui.QMenu()

            # context menu > reload
            self.UI_report_contextmenu.addAction(QtGui.QAction(
                "Reload", self, triggered=self.on_report_reload
            ))

            # context menu > close
            self.UI_report_contextmenu.addAction(QtGui.QAction(
                "Close", self, triggered=self.on_report_close
            ))

            return reportsD

        def create_plot():
            """Create the plot."""
            self.UI_figure = Figure()
            self.UI_canvas = FigureCanvas(self.UI_figure)

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
        self.splitDockWidget(plotD, infoD, QtCore.Qt.Vertical)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tableD)
        self.tabifyDockWidget(plotD, tableD)
        plotD.raise_()

        self.show()

        self.UI_setting -= 1

    def UI_settings_load(self):
        """Load Qt settings."""
        settings = QtCore.QSettings("HPAC", "ELAPS:Viewer")
        state = eval(str(settings.value("state", type=str)))
        self.stats_showing, self.metric_showing = state
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

    # report routines
    def report_load(self, filename, UI_alert=False):
        """Load a report."""
        filename = os.path.relpath(filename)
        reportid = os.path.abspath(filename)

        # load report
        try:
            report = elaps.io.load_report(filename)
        except:
            if UI_alert:
                self.UI_alert("ERROR: Can't load %r" % filename)
            else:
                self.alert("ERROR: Can't load %r" % filename)
            return
        self.reports[reportid] = report

        # set colors
        for callid in sorted(report.callids):
            self.report_colors[reportid, callid] = self.colorpool.pop()

        self.log("Loaded %r" % filename)
        return

    def report_reload(self, reportid):
        """Reload a report."""
        filename = reportid
        try:
            report = elaps.io.load_report(filename)
        except:
            if UI_alert:
                self.UI_alert("ERROR: Can't reload %r" % filename)
            else:
                self.alert("ERROR: Can't reload %r" % filename)
            return

        # set colors
        for callid in self.reports[reportid].callids:
            if callid not in report.callids:
                self.colorpool.append(self.report_colors[reportid, callid])
                del self.report_colors[reportid, callid]
        for callid in report.callids:
            if callid not in self.reports[reportid].callids:
                self.report_colors[reportid, callid] = self.colorpool.pop()

        self.reports[reportid] = report

    def report_close(self, reportid):
        """Close a report."""
        for callid in report.callids:
            self.colorpool.append(self.report_colors[reportid, callid])
            del self.report_colors[reportid, callid]

    # UI setters
    def UI_setall(self):
        """Set all UI elements."""
        self.UI_stats_set()
        self.UI_reports_set()
        self.UI_table_set()
        self.UI_reports_resizecolumns()
        # TODO

    def UI_stats_set(self):
        """Set UI element: stats."""
        self.UI_setting += 1
        for stat_name, stat in self.UI_stats:
            stat.setChecked(stat_name in self.stats_showing)
        self.UI_setting -= 1

    def UI_reports_set(self):
        """Set UI elemnt: reports."""
        self.UI_setting += 1
        for reportid, report in self.reports.items():
            ex = report.experiment
            # create or get the report item
            if reportid not in self.UI_reports.reports:
                UI_report = QtGui.QTreeWidgetItem(
                    (os.path.basename(reportid)[:-4], "", "", "", ""),
                )
                UI_report.setFlags(QtCore.Qt.ItemIsSelectable |
                                   QtCore.Qt.ItemIsEnabled)
                UI_report.reportid = reportid
                UI_report.callid = None
                UI_report.calls = {None: UI_report}

                self.UI_reports.addTopLevelItem(UI_report)
                self.UI_reports.reports[reportid] = UI_report

                # tooltip
                UI_report.setToolTip(0, os.path.relpath(reportid))

                # showing
                UI_showing = QtGui.QCheckBox(
                    toggled=self.on_report_showing_change
                )
                UI_showing.item = UI_report
                self.UI_reports.setItemWidget(UI_report, 1, UI_showing)
                UI_report.showing = UI_showing

                # color
                UI_color = QtGui.QPushButton(
                    clicked=self.on_report_color_change
                )
                UI_color.item = UI_report
                self.UI_reports.setItemWidget(UI_report, 2, UI_color)
                UI_report.color = UI_color
            else:
                UI_report = self.UI_reports.reports[reportid]

            # create new calls
            for callid in report.callids:
                if callid not in UI_report.calls:
                    UI_call = QtGui.QTreeWidgetItem(("",))
                    UI_call.reportid = reportid
                    UI_call.callid = callid

                    UI_report.addChild(UI_call)
                    UI_report.calls[callid] = UI_call

                    # showing
                    UI_showing = QtGui.QCheckBox(
                        toggled=self.on_report_showing_change
                    )
                    UI_showing.item = UI_call
                    self.UI_reports.setItemWidget(UI_call, 1, UI_showing)
                    UI_call.showing = UI_showing

                    # color
                    UI_color = QtGui.QPushButton(
                        clicked=self.on_report_color_change
                    )
                    UI_color.item = UI_call
                    self.UI_reports.setItemWidget(UI_call, 2, UI_color)
                    UI_call.color = UI_color

            # delete excess calls
            for callid, UI_call in UI_report.calls.items():
                if callid not in report.callids:
                    UI_report.takeChild(UI_report.indexOfChild(UI_call))
                    del UI_report.calls[callid]

            # set values
            UI_report.setToolTip(3, ex.sampler["cpu_model"])
            for callid in report.callids:
                UI_item = UI_report.calls[callid]

                # values
                if callid is None:
                    UI_item.setText(3, ex.sampler["system_name"])
                    UI_item.setText(4, ex.sampler["blas_name"])
                else:
                    call = ex.calls[callid]
                    UI_item.setText(0, call[0])
                    UI_item.setToolTip(0, str(call))

                # widgets
                UI_item.showing.setChecked(
                    (reportid, callid) in self.reports_showing
                )
                color = self.report_colors[reportid, callid]
                UI_item.color.pyqtConfigure(
                    styleSheet="background-color: %s;" % color,
                    toolTip=color
                )

        # delete excess calls
        for reportid, UI_report in self.UI_reports.reports.items():
            if reportid not in self.reports:
                self.UI_reports.takeTopLevelItem(
                    self.UI_reports.indexOfTopLevelItem(UI_report)
                )
                del self.UI_reports.reports[reportid]
        self.UI_setting -= 1

    def UI_info_set(self):
        """Set UI element: info."""
        self.UI_setting += 1
        reportid, callid = self.reportitem_selected
        if reportid is None:
            self.UI_setting -= 1
            return
        self.UI_info.setWindowTitle("Report %s" % os.path.relpath(reportid))
        self.UI_info.widget().setText(
            str(self.reports[reportid].experiment)
        )
        self.UI_setting -= 1

    def UI_table_set(self):
        """Set UI element: table."""
        # TODO

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
            self.Qapp.playmat.UI_window.close()
        self.Qapp.quit()

    def closeEvent(self, event):
        """Event: close main window."""
        settings = QtCore.QSettings("HPAC", "ELAPS:Viewer")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        state = self.stats_showing, self.metric_showing
        settings.setValue("state", repr(state))

    @pyqtSlot()
    def on_playmat_start(self):
        """Event: start PlayMat."""
        # TODO

    @pyqtSlot(bool)
    def on_stat_toggle(self, checked):
        """Event: stat toggled."""
        if self.UI_setting:
            return
        self.stats_showing = [stat_name for stat_name, stat in self.UI_stats
                              if stat.isChecked()]
        # TODO

    @pyqtSlot(str)
    def on_metric_change(self, value):
        """Event: metric changed."""
        self.metric_showing = str(value)
        # TODO

    @pyqtSlot()
    def on_report_load(self):
        """Event: load Report."""
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Load Experiment", elaps.io.reportpath, "*.eer"
        )
        if not filename:
            return
        reportid = self.report_load(str(filename))
        # TODO

    def on_reports_dragenter(self, event):
        """Event: drag into report list."""
        for url in event.mimeData().urls():
            if str(url.toLocalFile())[-4:] == ".eer":
                event.acceptProposedAction()
                return

    def on_reports_dragmove(self, event):
        """Event: Dragging in report list."""
        self.Qt_reports_dragenter(Qevent)

    def on_reports_drop(self, event):
        """Event: drop files in report list."""
        for url in Qevent.mimeData().urls():
            filename = str(url.toLocalFile())
            if filename[-4:] == ".emr":
                self.report_load(filename, True)
        # TODO update

    @pyqtSlot(QtCore.QPoint)
    def on_report_contextmenu_show(self, pos):
        """Event: right click on reports."""
        item = self.UI_reports.itemAt(pos)
        if not item:
            return
        globalpos = self.UI_reports.viewport().mapToGlobal(pos)
        self.UI_report_contextmenu.reportid = item.reportid
        self.UI_report_contextmenu.exec_(globalpos)

    @pyqtSlot()
    def on_report_reload(self):
        """Event: reload Report."""
        # TODO

    @pyqtSlot()
    def on_report_close(self):
        """Event: close Report."""
        # TODO

    @pyqtSlot(QtGui.QTreeWidgetItem, QtGui.QTreeWidgetItem)
    def on_report_select(self, current, previous):
        """Event: select Report."""
        self.reportitem_selected = (current.reportid, current.callid)
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

    # @pyqtSlot(bool)  # sender() pyqt bug
    def on_report_showing_change(self, checked):
        """Event: toggled report showing."""
        if self.UI_setting:
            return
        item = self.Qapp.sender().item
        if checked:
            self.reports_showing.add((item.reportid, item.callid))
        else:
            self.reports_showing.discard((item.reportid, item.callid))
        # TODO

    # @pyqtSlot()  # sender() pyqt bug
    def on_report_color_change(self):
        """Event: change report item color."""
        item = self.Qapp.sender().item
        Qcolor = QtGui.QColorDialog.getColor(QtGui.QColor(
            self.report_colors[item.reportid, item.callid]
        ))
        if Qcolor.isValid():
            self.report_colors[item.reportid, item.callid] = str(Qcolor.name())
        self.UI_reports_set()
        # TODO
