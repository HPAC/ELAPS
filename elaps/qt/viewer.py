#!/usr/bin/env python
"""GUI for Reports."""
from __future__ import division, print_function

import elaps.io
import elaps.plot

import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot


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

        # load some stuff
        self.papi_names = elaps.io.load_papinames()
        self.metrics = elaps.io.load_all_metrics()

        # set up UI
        self.UI_init()
        self.stats_showing = ["med"]
        self.metric_showing = ["Gflops/s"]
        if "reset" not in kwargs or not kwargs["reset"]:
            try:
                self.UI_settings_load()
            except:
                pass

        # load reports
        self.reports = {}
        for filename in filenames:
            try:
                report = elaps.io.load_report(filename)
                self.report_add(report)
            except:
                self.alerT("ERROR: Can't load %r" % filename)

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

            # stats
            self.statsT = self.addToolBar("Statistics")
            self.statsT.pyqtConfigure(movable=False, objectName="Statistics")
            self.statsT.stats = {}
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
                self.statsT.addWidget(stat)
                stat.stat_name = stat_name
                self.statsT.stats[stat_name] = stat

        def create_reports():
            self.UI_reports = QtGui.QTreeWidget(
                acceptDrops=True,
                currentItemChanged=self.on_report_select,
                itemExpanded=self.on_report_expand
            )
            self.UI_reports.dragEnterEvent = self.on_reports_dragenter
            self.UI_reports.dragMoveEvent = self.on_reports_dragmove
            self.UI_reports.dropEvent = self.on_reports_drop
            self.UI_reports.setHeaderLabels(
                ("report", "", "color", "system", "#t", "blas")
            )

            reportsD = QtGui.QDockWidget(
                "Reports",
                objectName="Reports",
                features=(QtGui.QDockWidget.DockWidgetFloatable |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            reportsD.setWidget(self.UI_reports)
            return reportsD

            # drop files

            # context menu
            self.Qt_reports.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.Qt_reports.customContextMenuRequested.connect(
                self.Qt_report_contextmenu_show
            )
            self.Qt_report_contextmenu = QtGui.QMenu()

            # context menu > reload
            reload_ = QtGui.QAction("Reload", self)
            self.Qt_report_contextmenu.addAction(reload_)
            reload_.triggered.connect(self.Qt_report_reload)

            # context menu > close
            close = QtGui.QAction("Close", self)
            self.Qt_report_contextmenu.addAction(close)
            close.triggered.connect(self.Qt_report_close)

            self.Qt_report_contextmenu.reportid = None

            self.Qt_Qreports = {}

            return reportsD

        create_menus()
        create_toolbar()
        reportsD = create_reports()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, reportsD)

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

    # setters
    def UI_setall(self):
        """Set all UI elements."""
        # TODO

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
        # TODO

    @pyqtSlot()
    def on_report_load(self):
        """Event: load Report."""
        # TODO

    def on_reports_dragenter(self, event):
        """Event: drag into report list."""
        # TODO

    def on_reports_dragmove(self, event):
        """Event: Dragging in report list."""
        # TODO

    def on_reports_drop(self, event):
        """Event: drop files in report list."""
        # TODO

    @pyqtSlot()
    def on_report_reload(self):
        """Event: reload Report."""
        # TODO

    @pyqtSlot()
    def on_report_close(self):
        """Event: close Report."""
        # TODO

    @pyqtSlot()
    def on_report_select(self):
        """Event: select Report."""
        # TODO

    @pyqtSlot()
    def on_report_expand(self):
        """Event: select Report."""
        # TODO
