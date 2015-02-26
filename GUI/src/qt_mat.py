#!/usr/bin/env python
"""Qt implementaiton of ELAPS:Mat."""
from __future__ import division, print_function

from mat import Mat
from qt_call import QCall
from qt_vary import QVary
import papi

import os
import sys

from PyQt4 import QtCore, QtGui


class QMat(Mat):

    """ELAPS:Mat implementation in Qt."""

    def __init__(self, app=None, loadstate=True):
        """Initialize the ELAPS:Mat."""
        if app:
            self.Qt_app = app
        else:
            self.Qt_app = QtGui.QApplication(sys.argv)
            self.Qt_app.viewer = None
        self.Qt_app.mat = self
        self.Qt_setting = 0
        self.Qt_initialized = False
        Mat.__init__(self, loadstate)

    def state_init(self, load=True):
        """Try to load the state and geometry."""
        if not load:
            Mat.state_init(self)
            return
        settings = QtCore.QSettings("HPAC", "ELAPS:Mat")
        self.Qt_setting += 1
        self.Qt_window.restoreGeometry(
            settings.value("geometry").toByteArray()
        )
        self.Qt_window.restoreState(
            settings.value("windowState").toByteArray()
        )
        self.Qt_setting -= 1
        try:
            self.state_fromstring(str(
                settings.value("appState").toString()
            ))
        except:
            Mat.state_init(self)

    def UI_init(self):
        """Initialize all GUI elements."""
        self.Qt_setting += 1

        # window
        self.Qt_window = QtGui.QMainWindow()
        window = self.Qt_window
        window.setWindowTitle("ELAPS:Mat")
        window.setUnifiedTitleAndToolBarOnMac(True)
        window.closeEvent = self.Qt_window_close
        window.setCorner(QtCore.Qt.TopRightCorner,
                         QtCore.Qt.RightDockWidgetArea)

        def create_menus():
            """Create all menus."""
            menu = window.menuBar()

            # file
            fileM = menu.addMenu("File")

            # file > submit
            self.Qt_submitA = QtGui.QAction("Run", window)
            fileM.addAction(self.Qt_submitA)
            self.Qt_submitA.setShortcut(QtGui.QKeySequence("Ctrl+R"))
            self.Qt_submitA.triggered.connect(self.Qt_submit_click)

            # file
            fileM.addSeparator()

            # file > reset
            reset = QtGui.QAction("Reset Setup", window)
            fileM.addAction(reset)
            reset.triggered.connect(self.Qt_state_reset_click)

            # file > load
            load = QtGui.QAction("Load Setup ...", window)
            fileM.addAction(load)
            load.setShortcut(QtGui.QKeySequence.Open)
            load.triggered.connect(self.Qt_state_load_click)

            # load report shortcut
            loadreport = QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+O"),
                window, self.Qt_state_reportload_click
            )

            # fie > save
            save = QtGui.QAction("Save Setup ...", window)
            fileM.addAction(save)
            save.setShortcut(QtGui.QKeySequence.Save)
            save.triggered.connect(self.Qt_state_save_click)

            # file
            fileM.addSeparator()

            viewer = QtGui.QAction("Start Viewer", window)
            fileM.addAction(viewer)
            viewer.triggered.connect(self.Qt_viewer_start_click)

            # ranges
            self.Qt_rangesM = menu.addMenu("Ranges")
            self.Qt_useranges = {}

            def userange_create(rangename, desc, group=None):
                """Create a userange option."""
                userange = QtGui.QAction(desc, window)
                self.Qt_useranges[rangename] = userange
                userange.setCheckable(True)
                userange.setActionGroup(group)
                userange.rangename = rangename
                userange.toggled.connect(self.Qt_userange_toggle)
                return userange

            groupouter = QtGui.QActionGroup(window)
            self.Qt_rangesM.addAction(
                userange_create("threads", "#threads range", groupouter)
            )
            self.Qt_rangesM.addAction(
                userange_create("range", "for each range", groupouter)
            )
            self.Qt_rangesM.addAction(userange_create(None, "none",
                                                      groupouter))
            self.Qt_rangesM.addSeparator()
            groupinner = QtGui.QActionGroup(window)
            self.Qt_rangesM.addAction(
                userange_create("sum", "sum over range", groupinner)
            )
            self.Qt_rangesM.addAction(
                userange_create("omp", "parallel range", groupinner))
            self.Qt_rangesM.addAction(userange_create(None, "none",
                                                      groupinner))

            # options
            optionsM = menu.addMenu("Options")
            self.Qt_options = {}

            def create_option(name, desc):
                """Create an option."""
                option = QtGui.QAction(desc, window)
                optionsM.addAction(option)
                self.Qt_options[name] = option
                option.setCheckable(True)
                option.optionname = name
                option.toggled.connect(self.Qt_option_toggle)

            create_option("papi", "use papi")
            create_option("header", "script header")
            create_option("vary", "vary matrices")
            create_option("omp", "calls in parallel")

            # view
            viewM = menu.addMenu("View")

            # view > showargs
            self.Qt_showargs = {}
            for name, desc in (
                ("flags", "show flag arguments"),
                ("scalars", "show scalar arguments"),
                ("lds", "show leading dimensions"),
                ("work", "show workspace arguments"),
                ("infos", "show info arguments")
            ):
                showarg = QtGui.QAction(desc, window)
                viewM.addAction(showarg)
                showarg.setCheckable(True)
                showarg.toggled.connect(self.Qt_showarg_toggle)
                showarg.argtype = name
                self.Qt_showargs[name] = showarg

            # view
            viewM.addSeparator()

            showinfo = QtGui.QAction("Show Sampler Info", window)
            viewM.addAction(showinfo)
            showinfo.triggered.connect(self.Qt_sampler_about_show)

        def create_sampler():
            """Create the sampler Toolbar."""
            samplerT = window.addToolBar("Sampler")
            samplerT.setMovable(False)
            samplerT.setObjectName("Sampler")
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            self.Qt_sampler = QtGui.QComboBox()
            samplerT.addWidget(self.Qt_sampler)
            self.Qt_sampler.addItems(sorted(self.samplers.keys()))
            self.Qt_sampler.currentIndexChanged.connect(self.Qt_sampler_change)

        def create_nt():
            """Create the #threads toolbar."""
            self.Qt_ntT = window.addToolBar("#threads")
            self.Qt_ntT.setMovable(False)
            self.Qt_ntT.setObjectName("#threads")
            self.Qt_ntT.addWidget(QtGui.QLabel("#threads:"))
            self.Qt_nt = QtGui.QComboBox()
            self.Qt_ntT.addWidget(self.Qt_nt)
            self.Qt_nt.currentIndexChanged.connect(self.Qt_nt_change)

        def create_infer_lds():
            self.Qt_infer_ldsT = window.addToolBar("infer lds")
            self.Qt_infer_ldsT.setMovable(False)
            self.Qt_infer_ldsT.setObjectName("infer lds")
            infer = QtGui.QPushButton("infer secondary dims")
            self.Qt_infer_ldsT.addWidget(infer)
            infer.clicked.connect(self.Qt_infer_lds_click)

        def create_submit():
            """Create the submit toolbar."""
            samplerT = window.addToolBar("Submit")
            samplerT.setMovable(False)
            samplerT.setObjectName("Submit")

            # spacer
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
            samplerT.addWidget(spacer)

            # submit
            self.Qt_submit = QtGui.QAction(self.Qt_app.style().standardIcon(
                QtGui.QStyle.SP_DialogOkButton
            ), "Run", window)
            samplerT.addAction(self.Qt_submit)
            self.Qt_submit.triggered.connect(self.Qt_submit_click)

        def create_ranges():
            """Create the ranges dock widget."""
            rangesD = QtGui.QDockWidget("Ranges")
            window.addDockWidget(QtCore.Qt.TopDockWidgetArea, rangesD)
            rangesD.setObjectName("Ranges")
            rangesD.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar)
            rangesW = QtGui.QWidget()
            rangesD.setWidget(rangesW)
            rangesW.setSizePolicy(
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
            )
            rangesL = QtGui.QVBoxLayout()
            rangesW.setLayout(rangesL)
            margins = list(rangesL.getContentsMargins())
            margins[1] = 12
            margins[3] = 8
            rangesL.setContentsMargins(*margins)
            rangesL.setSpacing(0)

            # context menu
            rangesW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            rangesW.customContextMenuRequested.connect(
                self.Qt_ranges_rightclick
            )

            self.Qt_ranges = {}

            def create_range(rangename, indent, prefix, showrangevar=True,
                             suffix=""):
                """Create a range."""
                rangeW = QtGui.QWidget()
                self.Qt_ranges[rangename] = rangeW
                layout = QtGui.QHBoxLayout()
                rangeW.setLayout(layout)
                layout.setContentsMargins(indent, 0, 12, 4)

                # prefix
                layout.addWidget(QtGui.QLabel(prefix))

                # rangevar
                rangevar = QtGui.QLineEdit()
                rangeW.rangevar = rangevar
                if showrangevar:
                    layout.addWidget(rangevar)
                rangevar.setFixedWidth(32)
                rangevar.setValidator(QtGui.QRegExpValidator(
                    QtCore.QRegExp("[a-zA-Z]+"), self.Qt_app
                ))
                rangevar.rangename = rangename
                rangevar.textChanged.connect(self.Qt_rangevar_change)

                # =
                if showrangevar:
                    layout.addWidget(QtGui.QLabel("="))

                # range
                Qrange = QtGui.QLineEdit()
                rangeW.range = Qrange
                layout.addWidget(Qrange)
                Qrange.rangename = rangename
                Qrange.textChanged.connect(self.Qt_range_change)

                # reps: allow only intergets
                if rangename == "reps":
                    Qrange.setFixedWidth(32)
                    Qrange.setValidator(QtGui.QRegExpValidator(
                        QtCore.QRegExp("[1-9][0-9]*"), self.Qt_app
                    ))

                layout.addWidget(QtGui.QLabel(suffix))

                # stretch
                layout.addStretch(1)

                # unused warning
                if rangename != "reps":
                    unused = QtGui.QLabel()
                    layout.addWidget(unused)
                    unused.setPixmap(unused.style().standardPixmap(
                        QtGui.QStyle.SP_MessageBoxWarning
                    ).scaledToHeight(Qrange.sizeHint().height()))
                    rangeW.unused = unused

                # close
                if rangename != "reps":
                    close = QtGui.QToolButton()
                    layout.addWidget(close)
                    close.setIcon(close.style().standardIcon(
                        QtGui.QStyle.SP_TitleBarCloseButton
                    ))
                    close.rangename = rangename
                    close.clicked.connect(self.Qt_range_close)
                    close.setStyleSheet("border: 0px;")

                return rangeW

            rangesL.addWidget(create_range(
                "threads", 0, "for nt = ", False, "(#threads)"
            ))
            rangesL.addWidget(create_range(
                "range", 0, "for"
            ))
            rangesL.addWidget(create_range(
                "reps", 16, "repeat", False, "times"
            ))
            rangesL.addWidget(create_range(
                "sum", 32, "sum over"
            ))
            rangesL.addWidget(create_range(
                "omp", 32, "in parallel"
            ))
            ompflag = QtGui.QLabel("in parallel:")
            rangesL.addWidget(ompflag)
            self.Qt_ranges["ompflag"] = ompflag
            ompflag.setContentsMargins(48, 0, 12, 0)

        def create_sampler_about():
            """Create the sampler info dock widget."""
            # about
            self.Qt_sampler_aboutD = QtGui.QDockWidget("Sampler")
            self.Qt_sampler_aboutD.setObjectName("About Sampler")
            self.Qt_sampler_aboutD.setFeatures(
                QtGui.QDockWidget.DockWidgetClosable |
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable |
                QtGui.QDockWidget.DockWidgetVerticalTitleBar
            )
            self.Qt_window.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                                         self.Qt_sampler_aboutD)
            self.Qt_sampler_aboutD.setFloating(True)
            self.Qt_sampler_aboutD.hide()
            self.Qt_sampler_about = QtGui.QLabel()
            self.Qt_sampler_aboutD.setWidget(self.Qt_sampler_about)
            self.Qt_sampler_about.setContentsMargins(4, 4, 4, 4)

        def create_header():
            """Create the script header dock widget."""
            self.Qt_headerD = QtGui.QDockWidget("Header")
            window.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                                 self.Qt_headerD)
            self.Qt_headerD.setObjectName("Header")
            self.Qt_headerD.setFeatures(
                QtGui.QDockWidget.DockWidgetClosable |
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable |
                QtGui.QDockWidget.DockWidgetVerticalTitleBar
            )
            self.Qt_headerD.closeEvent = self.Qt_header_close
            self.Qt_header = QtGui.QPlainTextEdit()
            self.Qt_headerD.setWidget(self.Qt_header)
            self.Qt_header.textChanged.connect(self.Qt_header_change)

        def create_counters():
            """Create the counters dock widget."""
            self.Qt_countersD = QtGui.QDockWidget("PAPI Counters")
            window.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                                 self.Qt_countersD)
            self.Qt_countersD.setObjectName("PAPI Coutners")
            self.Qt_countersD.closeEvent = self.Qt_counters_close
            self.Qt_counters = QtGui.QWidget()
            self.Qt_countersD.setWidget(self.Qt_counters)
            self.Qt_counters.setLayout(QtGui.QVBoxLayout())
            self.Qt_counters.setSizePolicy(
                QtGui.QSizePolicy.Minimum,
                QtGui.QSizePolicy.Fixed
            )
            self.Qt_Qcounters = []

        def create_vary():
            """Create the vary dock widget."""
            self.Qt_varyD = QtGui.QDockWidget("Vary Matrices")
            window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.Qt_varyD)
            self.Qt_varyD.setObjectName("Vary Matrices")
            self.Qt_varyD.dockLocationChanged.connect(self.Qt_vary_move)
            self.Qt_varyD.closeEvent = self.Qt_vary_close
            varySA = QtGui.QScrollArea()
            self.Qt_varyD.setWidget(varySA)
            self.Qt_vary = QtGui.QWidget()
            varySA.setWidget(self.Qt_vary)
            varySA.setWidgetResizable(True)
            varyL = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
            self.Qt_vary.setLayout(varyL)
            varyL.insertStretch(100, 1)
            self.Qt_Qvarys = {}

        def create_calls():
            """Create the calls list and add button (central widget)."""
            centralW = QtGui.QWidget()
            window.setCentralWidget(centralW)
            centralL = QtGui.QVBoxLayout()
            centralL.setContentsMargins(0, 0, 0, 0)
            centralW.setLayout(centralL)
            self.Qt_calls = QtGui.QListWidget()
            centralL.addWidget(self.Qt_calls)
            self.Qt_calls.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
            self.Qt_calls.model().layoutChanged.connect(self.Qt_calls_reorder)
            self.Qt_calls.focusOutEvent = self.Qt_calls_focusout

            # add
            add = QtGui.QPushButton("+")
            centralL.addWidget(add)
            add.clicked.connect(self.Qt_call_add_click)
            add.setShortcut(QtGui.QKeySequence.New)

        def create_jobprogress():
            """Create the job pgoress dock widget."""
            self.Qt_jobprogressD = QtGui.QDockWidget("Job Progress")
            window.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                                 self.Qt_jobprogressD)
            self.Qt_jobprogressD.setObjectName("Job Progress")
            self.Qt_jobprogressD.hide()
            self.Qt_jobprogress = QtGui.QWidget()
            self.Qt_jobprogressD.setWidget(self.Qt_jobprogress)
            self.Qt_jobprogress.setSizePolicy(
                QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
            )
            layout = QtGui.QGridLayout()
            self.Qt_jobprogress.setLayout(layout)

            self.Qt_jobprogress_items = {}

            # timer
            self.Qt_jobprogress_timer = QtCore.QTimer()
            self.Qt_jobprogress_timer.setInterval(1000)
            self.Qt_jobprogress_timer.timeout.connect(
                self.UI_jobprogress_update
            )

        def create_statusbar():
            """Create the staus bar."""
            self.Qt_statusbar = window.statusBar()

        def create_style():
            """Set style options."""
            # stylesheet
            self.Qt_app.setStyleSheet("""
                QLineEdit[invalid="true"],
                *[invalid="true"] QLineEdit {
                    background: #FFDDDD;
                }
            """)

            palette = self.Qt_app.palette()
            dark = palette.text().color()
            darka = palette.text().color()
            darka.setAlpha(63)
            # pens and brushes (for dataargs)
            self.Qt_pens = {
                None: QtGui.QColor(0, 0, 255, 0),
                "maxfront": darka,
                "maxback": QtGui.QPen(darka, 0, QtCore.Qt.DashLine),
                "minfront": dark,
                "minback": QtGui.QPen(dark, 0, QtCore.Qt.DashLine)
            }
            window = palette.window().color()
            windowa = palette.window().color()
            windowa.setAlpha(63)
            self.Qt_brushes = {
                "max": windowa,
                "min": window
            }

        create_menus()
        create_sampler()
        create_nt()
        create_infer_lds()
        create_submit()
        create_ranges()
        create_sampler_about()
        create_header()
        create_counters()
        create_vary()
        create_calls()
        create_jobprogress()
        create_statusbar()
        create_style()
        window.show()

        self.Qt_setting -= 1
        self.Qt_initialized = True

    def UI_start(self):
        """Start the Mat (main loop)."""
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
        Mat.log(*args)

    def alert(self, *args):
        """Also log alert messages to status."""
        self.UI_setstatus(" ".join(map(str, args)))
        Mat.alert(*args)

    # dialogs
    def UI_alert(self, *args, **kwargs):
        """Show an alert message to the user."""
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_setstatus(self, msg, timeout=0):
        """Set the status message."""
        if self.Qt_initialized:
            self.Qt_statusbar.showMessage(msg, timeout)

    def UI_dialog(self, msgtype, title, text, callbacks=None):
        """Show a simple user dialog with multiple options."""
        if callbacks is None:
            callbacks = {"Ok": None}
        msgtypes = {
            "information": QtGui.QMessageBox.information,
            "warning": QtGui.QMessageBox.warning,
            "question": QtGui.QMessageBox.question,
            "critical": QtGui.QMessageBox.question
        }
        buttontypes = {
            "Ok": QtGui.QMessageBox.Ok,
            "Cancel": QtGui.QMessageBox.Cancel
        }

        callbackmap = {}
        buttons = 0
        for key, callback in callbacks.iteritems():
            callbackmap[buttontypes[key]] = callback
            buttons |= buttontypes[key]

        ret = msgtypes[msgtype](self.Qt_window, title, text, buttons)
        if callbackmap[ret] is not None:
            callbackmap[ret][0](*callbackmap[ret][1])

    # setters
    def UI_sampler_set(self):
        """Set the sampler."""
        self.Qt_setting += 1
        self.Qt_sampler.setCurrentIndex(
            self.Qt_sampler.findText(self.samplername)
        )
        self.Qt_setting -= 1

    def UI_sampler_about_set(self):
        """Set the sampler info string."""
        self.Qt_sampler_about.setText(self.sampler_about_str())

    def UI_nt_setmax(self):
        """Set the maximum #threads."""
        self.Qt_setting += 1
        self.Qt_nt.clear()
        self.Qt_nt.addItems(map(str, range(1, self.sampler["nt_max"] + 1)))
        self.Qt_setting -= 1

    def UI_nt_set(self):
        """Set the #threads."""
        self.Qt_setting += 1
        self.Qt_nt.setCurrentIndex(self.nt - 1)
        self.Qt_setting -= 1

    def UI_useranges_set(self):
        """Set which ranges are used."""
        self.Qt_setting += 1
        for rangetype, rangenames in self.rangetypes.iteritems():
            selected = self.userange[rangetype] is not None
            for rangename in rangenames:
                active = rangename == self.userange[rangetype]
                self.Qt_useranges[rangename].setChecked(active)
                self.Qt_ranges[rangename].setVisible(active)
        self.Qt_ntT.setVisible(self.userange["outer"] != "threads")
        self.Qt_setting -= 1

    def UI_options_set(self):
        """Set which options are used."""
        self.Qt_setting += 1
        self.Qt_options["papi"].setEnabled(
            self.sampler["papi_counters_max"] > 0
        )
        self.Qt_options["omp"].setEnabled(self.userange["inner"] != "omp" and
                                          self.sampler["omp_enabled"])
        for optionname, val in self.options.iteritems():
            self.Qt_options[optionname].setChecked(val)
        if self.userange["inner"] == "omp":
            self.Qt_options["omp"].setChecked(True)
        # other option effects
        self.Qt_countersD.setVisible(self.options["papi"])
        self.Qt_varyD.setVisible(self.options["vary"])
        self.Qt_headerD.setVisible(self.options["header"])
        self.Qt_ranges["ompflag"].setVisible(self.options["omp"] and
                                             self.userange["inner"] != "omp")
        self.Qt_setting -= 1

    def UI_showargs_set(self):
        """Set which arguments are shown."""
        self.Qt_setting += 1
        for name in self.Qt_showargs:
            self.Qt_showargs[name].setChecked(self.showargs[name])
        self.Qt_infer_ldsT.setVisible(self.showargs["lds"] or
                                      self.showargs["work"])
        self.Qt_setting -= 1

    def UI_header_set(self):
        """Set if the script header is used."""
        self.Qt_setting += 1
        self.Qt_header.setPlainText(self.header)
        self.Qt_setting -= 1

    def UI_counters_setoptions(self):
        """Set the available counter elements."""
        # delete old
        for Qcounter in self.Qt_Qcounters:
            Qcounter.deleteLater()

        # add new
        layout = self.Qt_counters.layout()
        for _ in range(self.sampler["papi_counters_max"]):
            Qcounter = QtGui.QComboBox()
            layout.addWidget(Qcounter)
            Qcounter.addItem("", QtCore.QVariant(""))
            for i, name in enumerate(self.sampler["papi_counters_avail"]):
                event = papi.events[name]
                Qcounter.addItem(event["short"], QtCore.QVariant(name))
                Qcounter.setItemData(i, name + "\n" + event["long"],
                                     QtCore.Qt.ToolTipRole)
            Qcounter.currentIndexChanged.connect(self.Qt_counter_change)

    def UI_counters_set(self):
        """Set the selected counters."""
        self.Qt_setting += 1
        for Qcounter, countername in zip(self.Qt_Qcounters, self.counters):
            index = Qcounter.findData(QtCore.QVariant(countername))
            Qcounter.setCurrentIndex(index)
            tip = ""
            if countername:
                tip = countername + "\n" + papi.events[countername]["long"]
            Qcounter.setToolTip(tip)
        self.Qt_setting -= 1

    def UI_ranges_set(self):
        """Set all ranges and their variables."""
        self.Qt_setting += 1
        for rangename in self.ranges:
            Qrange = self.Qt_ranges[rangename]
            Qrange.rangevar.setText(self.rangevars[rangename])
            Qrange.range.setText(str(self.ranges[rangename]))
        self.Qt_setting -= 1

    def UI_range_unusedalerts_set(self):
        """Set the unused alerts for all ranges appropriately."""
        for rangename, usage in self.ranges_checkuseage().iteritems():
            Qrange = self.Qt_ranges[rangename]
            Qrange.unused.setVisible(not usage)
            if not usage:
                Qrange.setToolTip("Warning: %r is not used." %
                                  self.rangevars[rangename])

    def UI_nrep_set(self):
        """Set the #repetitions."""
        self.Qt_setting += 1
        text = str(self.nrep) if self.nrep is not None else ""
        self.Qt_ranges["reps"].range.setText(text)
        self.Qt_setting -= 1

    def UI_vary_init(self):
        """Set the vary options for all operands."""
        # delete old
        for Qvary in self.Qt_Qvarys.values():
            Qvary.deleteLater()
        # add new
        self.Qt_Qvarys.clear()
        layout = self.Qt_vary.layout()
        for i, name in enumerate(sorted(self.data)):
            Qvary = QVary(self, name)
            layout.insertWidget(i, Qvary)
            self.Qt_Qvarys[name] = Qvary
        self.UI_vary_set()

    def UI_vary_set(self, name=None, resize=True):
        """Set the vary options for all operands."""
        if name is None:
            for name in self.Qt_Qvarys:
                self.UI_vary_set(name, False)
        else:
            self.Qt_Qvarys[name].set()
        if not resize:
            return
        # TODO: delay this
        width = height = 0
        for Qvary in self.Qt_Qvarys.values():
            size = Qvary.minimumSizeHint()
            width = max(width, size.width())
            height = max(height, size.height())
        margins = map(sum, zip(
            self.Qt_varyD.getContentsMargins(),
            self.Qt_varyD.widget().getContentsMargins(),
            self.Qt_varyD.widget().widget().getContentsMargins(),
            self.Qt_varyD.widget().widget().layout().getContentsMargins()
        ))
        width += margins[0] + margins[2]
        height += margins[1] + margins[3]
        self.Qt_varyD.setMinimumSize(width, height)

    def UI_calls_init(self):
        """Initialize all calls."""
        self.Qt_setting += 1
        # delete old
        self.Qt_calls.clear()
        # add new
        for callid in range(len(self.calls)):
            self.UI_call_add(callid)
        self.Qt_setting -= 1

    def UI_call_add(self, callid=None):
        """Add a call."""
        if callid is None:
            callid = len(self.calls) - 1
        Qcall = QCall(self, callid)
        self.Qt_calls.addItem(Qcall)
        Qcall.args_set()
        self.Qt_calls.setItemWidget(Qcall, Qcall.widget)

    def UI_call_set(self, callid, fromargid=None):
        """Set a call."""
        self.Qt_setting += 1
        self.Qt_calls.item(callid).args_set(fromargid)
        self.Qt_setting -= 1

    def UI_calls_set(self, fromcallid=None, fromargid=None):
        """Set all calls' arguments."""
        self.Qt_setting += 1
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).args_set(
                fromargid if fromcallid == callid else None
            )
        self.Qt_setting -= 1

    def UI_data_viz(self):
        """Update operand visualization."""
        self.Qt_setting += 1
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).data_viz()
        self.Qt_setting -= 1

    def UI_showargs_apply(self):
        """Apply which argument types are shown."""
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).showargs_apply()
        self.Qt_infer_ldsT.setVisible(self.showargs["lds"] or
                                      self.showargs["work"])

    def UI_arg_setfocus(self, callid, argid):
        """Set the focus to an argument."""
        self.Qt_calls.item(callid).Qt_args[argid].setFocus()

    def UI_submit_setenabled(self):
        """Enabled or disable the submit buttons."""
        enabled = self.calls_checksanity()
        self.Qt_submit.setEnabled(enabled)
        self.Qt_submitA.setEnabled(enabled)

    def UI_jobprogress_update(self):
        """Update the jobprogress widget."""
        if not self.Qt_jobprogress.isVisible():
            self.Qt_jobprogress_timer.stop()
            return
        self.jobprogress_update()
        # delete missing
        for jobid in self.Qt_jobprogress_items:
            if jobid not in self.jobprogress:
                for Qwidget in self.Qt_jobprogress_items[jobid]:
                    Qwidget.deleteLater()
        self.Qt_jobprogress_items = {
            jobid: Qitems
            for jobid, Qitems in self.Qt_jobprogress_items.iteritems()
            if jobid in self.jobprogress
        }
        for jobid in self.jobprogress:
            job = self.jobprogress[jobid]
            if jobid not in self.Qt_jobprogress_items:
                layout = self.Qt_jobprogress.layout()
                row = layout.rowCount()
                Qname = QtGui.QLabel(os.path.basename(job["filebase"]))
                layout.addWidget(Qname, row, 0)
                Qbar = QtGui.QProgressBar()
                layout.addWidget(Qbar, row, 1)
                Qbar.setRange(0, job["progressend"])
                Qlabel = QtGui.QLabel()
                layout.addWidget(Qlabel, row, 2)
                Qbutton = QtGui.QPushButton("kill")
                layout.addWidget(Qbutton, row, 3)
                Qbutton.clicked.connect(self.Qt_jobprogress_click)
                Qbutton.jobid = jobid
                Qhide = QtGui.QToolButton()
                layout.addWidget(Qhide, row, 4)
                Qhide.setIcon(Qhide.style().standardIcon(
                    QtGui.QStyle.SP_TitleBarCloseButton
                ))
                Qhide.jobid = jobid
                Qhide.clicked.connect(self.Qt_jobprogress_hide)
                Qhide.setStyleSheet("border: 0px;")
                self.Qt_jobprogress_items[jobid] = (Qname, Qbar, Qlabel,
                                                    Qbutton, Qhide)
            else:
                _, Qbar, Qlabel, Qbutton, _ = self.Qt_jobprogress_items[jobid]
            Qbar.setValue(min(max(0, job["progress"]), job["progressend"]))
            if job["error"]:
                Qlabel.setText("error")
            elif job["progress"] < 0:
                Qlabel.setText("pending")
            elif job["progress"] <= job["progressend"]:
                Qlabel.setText("%d / %d results"
                               % (job["progress"], job["progressend"]))
            else:
                Qlabel.setText("completed")
                Qbutton.setText("view")

    def UI_jobprogress_show(self):
        """Show the jobpgoress and start its automatic updates."""
        self.Qt_jobprogressD.hide()
        self.Qt_jobprogressD.show()
        self.UI_jobprogress_update()
        self.Qt_jobprogress_timer.start()

    def UI_viewer_start(self):
        """Start the Viewer."""
        from qt_mpl_viewer import QMPLViewer
        QMPLViewer(self.Qt_app)

    def UI_viewer_load(self, filename):
        """Load a report in the viewer."""
        if self.Qt_app.viewer is None:
            self.UI_viewer_start()
        self.Qt_app.viewer.UI_report_load(filename)
        self.UI_viewer_show()

    def UI_viewer_show(self):
        """Show the viewer (pull to front)."""
        self.Qt_app.viewer.Qt_window.show()

    # event handlers
    def Qt_console_quit(self, *args):
        """Event: Ctrl-C from the console."""
        print("\r", end="")
        self.Qt_window.close()
        if self.Qt_app.viewer:
            self.Qt_app.viewer.Qt_window.close()
        self.Qt_app.quit()

    def Qt_window_close(self, event):
        """Event: Main window closed."""
        settings = QtCore.QSettings("HPAC", "ELAPS:Mat")
        settings.setValue("geometry", self.Qt_window.saveGeometry())
        settings.setValue("windowState", self.Qt_window.saveState())
        settings.setValue("appState",
                          QtCore.QVariant(repr(self.state_toflat())))
        self.log("Setup saved.")

    def Qt_viewer_start_click(self):
        """Event: Start ELAPS:Viewer."""
        self.UI_viewer_start()

    def Qt_submit_click(self):
        """Event: Submit."""
        filename = QtGui.QFileDialog.getSaveFileName(
            self.Qt_window,
            "Generate Report",
            self.reportpath,
            "*.emr"
        )
        if filename:
            self.UI_submit(str(filename))

    def Qt_state_reset_click(self):
        """Event: Reset state."""
        self.UI_state_reset()

    def Qt_state_load_click(self, report=False):
        """Event: Load state."""
        filename = QtGui.QFileDialog.getOpenFileName(
            self.Qt_window,
            "Load Setup",
            self.reportpath if report else self.setuppath,
            "*.emr *.ems"
        )
        if filename:
            self.UI_state_import(str(filename))

    def Qt_state_reportload_click(self):
        """Event: Load state from report folder."""
        self.Qt_state_load_click(True)

    def Qt_state_save_click(self):
        """Event: Save state."""
        filename = QtGui.QFileDialog.getSaveFileName(
            self.Qt_window,
            "Save Setup",
            self.setuppath,
            "*.ems"
        )
        if filename:
            self.UI_state_export(str(filename))

    def Qt_sampler_change(self):
        """Event: Set the sampler."""
        if self.Qt_setting:
            return
        try:
            value = str(self.Qt_sampler.currentText())
        except:
            return
        self.UI_sampler_change(value)

    def Qt_sampler_about_show(self):
        """Event: Show the sampler info."""
        self.Qt_sampler_aboutD.show()

    def Qt_nt_change(self):
        """Event: Set the #threads."""
        if self.Qt_setting:
            return
        self.UI_nt_change(int(self.Qt_nt.currentText()))

    def Qt_infer_lds_click(self):
        """Event: Infer leading dimensions."""
        self.UI_infer_lds()

    def Qt_userange_toggle(self, checked):
        """Event: Change the used ranges."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        value = rangename if checked else None
        if rangename in self.rangetypes["outer"]:
            self.UI_userange_change("outer", value)
        else:
            self.UI_userange_change("inner", value)

    def Qt_ranges_rightclick(self, pos):
        """Event: Richt click on ranges."""
        sender = self.Qt_app.sender()
        pos = sender.mapToGlobal(pos)
        self.Qt_rangesM.exec_(pos)

    def Qt_range_close(self):
        """Event: Closed a range."""
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        if rangename in self.rangetypes["outer"]:
            self.UI_userange_change("outer", None)
        else:
            self.UI_userange_change("inner", None)

    def Qt_option_toggle(self, checked):
        """Event: Toggle an option."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        optionname = sender.optionname
        self.UI_option_change(optionname, checked)

    def Qt_showarg_toggle(self, checked):
        """Event: Change what arguments to show."""
        if self.Qt_setting:
            return
        argtype = self.Qt_app.sender().argtype
        self.UI_showargs_change(argtype, checked)

    def Qt_counters_close(self, event):
        """Event: Closed the counters window."""
        if self.Qt_setting:
            return
        self.UI_option_change("papi", False)

    def Qt_counter_change(self):
        """Event: Changed a counter."""
        if self.Qt_setting:
            return
        counternames = []
        for Qcounter in self.Qt_Qcounters:
            countername = str(
                Qcounter.itemData(Qcounter.currentIndex()).toString()
            )
            counternames.append(countername if countername else None)
            tip = ""
            if countername:
                tip = countername + "\n" + papi.events[countername]["long"]
            Qcounter.setToolTip(tip)
        self.UI_counters_change(counternames)

    def Qt_vary_move(self, area):
        """The vary dock moved to a different area."""
        if area in (QtCore.Qt.TopDockWidgetArea,
                    QtCore.Qt.BottomDockWidgetArea):
            direction = QtGui.QBoxLayout.LeftToRight
        else:
            direction = QtGui.QBoxLayout.TopToBottom
        self.Qt_vary.layout().setDirection(direction)

    def Qt_vary_close(self, event):
        """Event: Closed the vary window."""
        if self.Qt_setting:
            return
        self.UI_option_change("vary", False)

    def Qt_header_change(self):
        """Event: Changed the script header."""
        try:
            text = str(self.Qt_header.toPlainText())
        except:
            return
        height = self.Qt_header.fontMetrics().lineSpacing()
        nlines = max(text.count("\n") + 1, 4)
        self.Qt_header.setFixedHeight(height * (nlines + 1))
        if self.Qt_setting:
            return
        self.UI_header_change(text)

    def Qt_header_close(self, event):
        """Event: Closed the script header."""
        if self.Qt_setting:
            return
        self.UI_option_change("header", False)

    def Qt_rangevar_change(self):
        """Event: Changed a range variable."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        try:
            value = str(sender.text())
        except:
            return
        self.UI_rangevar_change(rangename, value)

    def Qt_range_change(self):
        """Event: Changed a range."""
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        try:
            value = str(sender.text())
        except:
            return
        if rangename == "reps":
            self.UI_nrep_change(value)
        else:
            self.UI_range_change(rangename, value)

    def Qt_call_add_click(self):
        """Event: Add a call."""
        self.UI_call_add_click()

    def Qt_calls_reorder(self):
        """Event: Reordered calls."""
        order = []
        for i in range(self.Qt_calls.count()):
            Qcall = self.Qt_calls.item(i)
            order.append(Qcall.callid)
            Qcall.callid = i
        self.UI_calls_reorder(order)

    def Qt_calls_focusout(self, event):
        """Event: Move the focues away from a call item."""
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.setItemSelected(self.Qt_calls.item(callid), False)

    def Qt_jobprogress_click(self):
        """Event: Clicked the button next to a job progress."""
        sender = self.Qt_app.sender()
        jobid = sender.jobid
        job = self.jobprogress[jobid]
        if job["progress"] <= job["progressend"]:
            self.UI_jobkill(jobid)
        else:
            self.UI_jobview(jobid)

    def Qt_jobprogress_hide(self):
        """Event: Hide job progress."""
        sender = self.Qt_app.sender()
        jobid = sender.jobid
        self.UI_jobprogress_hide(jobid)


def main():
    """Main routine to start a Qt based Sampler."""
    loadstate = "--reset" not in sys.argv[1:]
    QMat(loadstate=loadstate).start()


if __name__ == "__main__":
    main()
