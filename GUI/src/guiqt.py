#!/usr/bin/env python
from __future__ import division, print_function

from gui import GUI
from qcall import QCall
import papi

import os
import sys

from PyQt4 import QtCore, QtGui


class GUI_Qt(GUI):
    def __init__(self, app=None, loadstate=True):
        if app:
            self.Qt_app = app
        else:
            self.Qt_app = QtGui.QApplication(sys.argv)
            self.Qt_app.viewer = None
        self.Qt_app.gui = self
        self.Qt_setting = 0
        self.Qt_initialized = False
        GUI.__init__(self, loadstate)

    def state_init(self, load=True):
        self.state_reset()
        if not load:
            return
        settings = QtCore.QSettings("HPAC", "Sampler")
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
            self.log("loaded previous state")
        except:
            pass

    def UI_init(self):
        self.Qt_setting += 1
        # window
        self.Qt_window = QtGui.QMainWindow()
        window = self.Qt_window
        window.setWindowTitle("Sampler")
        window.setUnifiedTitleAndToolBarOnMac(True)
        window.closeEvent = self.Qt_window_close

        def create_menus():
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
            load = QtGui.QAction("Import Setup ...", window)
            fileM.addAction(load)
            load.triggered.connect(self.Qt_state_load_click)

            # file
            fileM.addSeparator()

            viewer = QtGui.QAction("Start Viewer", window)
            fileM.addAction(viewer)
            viewer.triggered.connect(self.Qt_viewer_start_click)

            # ranges
            rangesM = menu.addMenu("Ranges")
            self.Qt_useranges = {}

            def userange_create(rangename, desc):
                userange = QtGui.QAction(desc, window)
                self.Qt_useranges[rangename] = userange
                userange.setCheckable(True)
                userange.rangename = rangename
                userange.toggled.connect(self.Qt_userange_toggle)
                return userange

            rangesM.addAction(userange_create("threads", "#threads range"))
            rangesM.addAction(userange_create("range", "for each range"))
            rangesM.addSeparator()
            rangesM.addAction(userange_create("sum", "sum over range"))
            rangesM.addAction(userange_create("omp", "parallel range"))

            # options
            optionsM = menu.addMenu("Options")
            self.Qt_options = {}

            def create_option(name, desc):
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
            samplerT = window.addToolBar("Sampler")
            samplerT.setMovable(False)
            samplerT.setObjectName("Sampler")
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            self.Qt_sampler = QtGui.QComboBox()
            samplerT.addWidget(self.Qt_sampler)
            self.Qt_sampler.addItems(sorted(self.samplers.keys()))
            self.Qt_sampler.currentIndexChanged.connect(self.Qt_sampler_change)

        def create_nt():
            self.Qt_ntT = window.addToolBar("#threads")
            self.Qt_ntT.setMovable(False)
            self.Qt_ntT.setObjectName("Sampler")
            self.Qt_ntT.addWidget(QtGui.QLabel("#threads:"))
            self.Qt_nt = QtGui.QComboBox()
            self.Qt_ntT.addWidget(self.Qt_nt)
            self.Qt_nt.currentIndexChanged.connect(self.Qt_nt_change)

        def create_submit():
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
            self.Qt_ranges = {}

            def create_range(rangename, indent, prefix, showrangevar=True,
                             suffix=""):
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
                    QtCore.QRegExp("[a-zA-Z]+"), self.Qt_app)
                )
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
                        QtCore.QRegExp("[1-9][0-9]*"), self.Qt_app)
                    )

                # stretch
                layout.addStretch(1)

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

        def create_sampler_about():
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

        def create_calls():
            centralW = QtGui.QWidget()
            window.setCentralWidget(centralW)
            centralL = QtGui.QVBoxLayout()
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
            self.Qt_jobprogressD = QtGui.QDockWidget("Job Progress")
            window.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                                 self.Qt_jobprogressD)
            self.Qt_jobprogressD.setObjectName("Job Progress")
            self.Qt_jobprogressD.hide()
            self.Qt_jobprogress = QtGui.QWidget()
            self.Qt_jobprogressD.setWidget(self.Qt_jobprogress)
            layout = QtGui.QGridLayout()
            self.Qt_jobprogress.setLayout(layout)

            # timer
            self.Qt_jobprogress_items = []
            self.Qt_jobprogress_timer = QtCore.QTimer()
            self.Qt_jobprogress_timer.setInterval(1000)
            self.Qt_jobprogress_timer.timeout.connect(
                self.UI_jobprogress_update
            )

        def create_statusbar():
            self.Qt_statusbar = window.statusBar()

        def create_style():
            # stylesheet
            self.Qt_app.setStyleSheet("""
                QLineEdit[invalid="true"],
                *[invalid="true"] QLineEdit {
                    background: #FFDDDD;
                }
                QScrollArea {
                    border: 0px;
                    background: palette(dark);
                }
                QScrollArea > * > QWidget {
                    background: palette(dark);
                }
                QScrollArea QCall {
                    background: palette(window);
                }
            """)

            palette = self.Qt_app.palette()
            dark = palette.text().color()
            darka = palette.text().color()
            darka.setAlpha(127)
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
            windowa.setAlpha(127)
            self.Qt_brushes = {
                "max": windowa,
                "min": window
            }

        create_menus()
        create_sampler()
        create_nt()
        create_submit()
        create_ranges()
        create_sampler_about()
        create_header()
        create_counters()
        create_calls()
        create_jobprogress()
        create_statusbar()
        create_style()
        window.show()

        self.Qt_setting -= 1
        self.Qt_initialized = True

    def UI_start(self):
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(self.Qt_app.exec_())

    # utility
    def log(self, *args):
        self.UI_setstatus(" ".join(map(str, args)), 2000)
        GUI.log(self, *args)

    def alert(self, *args):
        self.UI_setstatus(" ".join(map(str, args)))
        GUI.alert(self, *args)

    # dialogs
    def UI_alert(self, *args, **kwargs):
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_setstatus(self, msg, timeout=0):
        if self.Qt_initialized:
            self.Qt_statusbar.showMessage(msg, timeout)

    def UI_dialog(self, msgtype, title, text, callbacks={"Ok": None}):
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
        self.Qt_setting += 1
        self.Qt_sampler.setCurrentIndex(
            self.Qt_sampler.findText(self.samplername)
        )
        self.Qt_setting -= 1

    def UI_sampler_about_set(self):
        self.Qt_sampler_about.setText(self.sampler_about_str())

    def UI_nt_setmax(self):
        self.Qt_setting += 1
        self.Qt_nt.clear()
        self.Qt_nt.addItems(map(str, range(1, self.sampler["nt_max"] + 1)))
        self.Qt_setting -= 1

    def UI_nt_set(self):
        self.Qt_setting += 1
        self.Qt_nt.setCurrentIndex(self.nt - 1)
        self.Qt_setting -= 1

    def UI_useranges_set(self):
        self.Qt_setting += 1
        for rangetype, rangenames in self.rangetypes.iteritems():
            selected = self.userange[rangetype] is not None
            for rangename in rangenames:
                active = rangename == self.userange[rangetype]
                self.Qt_useranges[rangename].setEnabled(active or not selected)
                self.Qt_useranges[rangename].setChecked(active)
                self.Qt_ranges[rangename].setVisible(active)
        self.Qt_ntT.setVisible(self.userange["outer"] != "threads")
        self.Qt_setting -= 1

    def UI_options_set(self):
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
        self.Qt_headerD.setVisible(self.options["header"])
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).usevary_apply()
        self.Qt_setting -= 1

    def UI_showargs_set(self, name=None):
        if name is None:
            for name in self.Qt_showargs:
                self.UI_showargs_set(name)
            return
        self.Qt_setting += 1
        self.Qt_showargs[name].setChecked(self.showargs[name])
        self.Qt_setting -= 1

    def UI_header_set(self):
        self.Qt_setting += 1
        self.Qt_header.setPlainText(self.header)
        self.Qt_setting -= 1

    def UI_counters_setoptions(self):
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
        self.Qt_setting += 1
        for rangename in self.ranges:
            Qrange = self.Qt_ranges[rangename]
            Qrange.rangevar.setText(self.rangevars[rangename])
            Qrange.range.setText(str(self.ranges[rangename]))
        self.Qt_setting -= 1

    def UI_nrep_set(self):
        self.Qt_setting += 1
        text = str(self.nrep) if self.nrep else ""
        self.Qt_ranges["reps"].range.setText(text)
        self.Qt_setting -= 1

    def UI_calls_init(self):
        self.Qt_setting += 1
        # delete old
        self.Qt_calls.clear()
        # add new
        for callid in range(len(self.calls)):
            self.UI_call_add(callid)
        self.Qt_setting -= 1

    def UI_call_add(self, callid=None):
        if callid is None:
            callid = len(self.calls) - 1
        Qcall = QCall(self, callid)
        self.Qt_calls.addItem(Qcall)
        self.Qt_calls.setItemWidget(Qcall, Qcall.widget)
        Qcall.args_set()

    def UI_call_set(self, callid, fromargid=None):
        self.Qt_setting += 1
        self.Qt_calls.item(callid).args_set(fromargid)
        self.Qt_setting -= 1

    def UI_calls_set(self, fromcallid=None, fromargid=None):
        self.Qt_setting += 1
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).args_set(
                fromargid if fromcallid == callid else None
            )
        self.Qt_setting -= 1

    def UI_data_viz(self):
        self.Qt_setting += 1
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).data_viz()
        self.Qt_setting -= 1

    def UI_showargs_apply(self):
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.item(callid).showargs_apply()

    def UI_arg_setfocus(self, callid, argid):
        self.Qt_calls.item(callid).Qt_args[argid].setFocus()

    def UI_submit_setenabled(self):
        enabled = self.calls_checksanity()
        self.Qt_submit.setEnabled(enabled)
        self.Qt_submitA.setEnabled(enabled)

    def UI_jobprogress_update(self):
        if not self.Qt_jobprogress.isVisible():
            self.Qt_jobprogress_timer.stop()
            return
        self.jobprogress_update()
        for i, job in enumerate(self.jobprogress):
            if not job and i < len(self.Qt_jobprogress_items):
                if self.Qt_jobprogress_items[i]:
                    for item in self.Qt_jobprogress_items[i]:
                        item.deleteLater()
                    self.Qt_jobprogress_items[i] = None
                continue
            layout = self.Qt_jobprogress.layout()
            if i >= len(self.Qt_jobprogress_items):
                name = os.path.basename(job["filebase"])
                Qname = QtGui.QLabel(name)
                layout.addWidget(Qname, i, 0)
                Qbar = QtGui.QProgressBar()
                layout.addWidget(Qbar, i, 1)
                Qbar.setRange(0, job["progressend"])
                Qlabel = QtGui.QLabel()
                layout.addWidget(Qlabel, i, 2)
                Qbutton = QtGui.QPushButton("kill")
                layout.addWidget(Qbutton, i, 3)
                Qbutton.clicked.connect(self.Qt_jobprogress_click)
                Qbutton.jobid = i
                self.Qt_jobprogress_items.append((Qname, Qbar, Qlabel,
                                                  Qbutton))
            else:
                Qname, Qbar, Qlabel, Qbutton = self.Qt_jobprogress_items[i]
            Qbar.setValue(min(max(0, job["progress"]), job["progressend"]))
            if job["error"]:
                Qlabel.setText("error")
            elif job["progress"] < 0:
                Qlabel.setText("pending")
            elif job["progress"] <= job["progressend"]:
                Qlabel.setText("%d / %d calls"
                               % (job["progress"], job["progressend"]))
            else:
                Qlabel.setText("completed")
                Qbutton.setText("view")

    def UI_jobprogress_show(self):
        self.Qt_jobprogressD.hide()
        self.Qt_jobprogressD.show()
        self.UI_jobprogress_update()
        self.Qt_jobprogress_timer.start()

    def UI_viewer_start(self):
        from viewerqtmpl import Viewer_Qt_MPL
        self.Qt_viewer = Viewer_Qt_MPL(self.Qt_app)

    def UI_viewer_load(self, filename):
        if self.Qt_app.viewer is None:
            self.UI_viewer_start()
        self.Qt_app.viewer.UI_report_load(filename)
        self.UI_viewer_show()

    def UI_viewer_show(self):
        self.Qt_app.viewer.Qt_window.show()

    # event handlers
    def Qt_window_close(self, event):
        settings = QtCore.QSettings("HPAC", "Sampler")
        settings.setValue("geometry", self.Qt_window.saveGeometry())
        settings.setValue("windowState", self.Qt_window.saveState())
        settings.setValue("appState",
                          QtCore.QVariant(repr(self.state_toflat())))

    def Qt_viewer_start_click(self):
        self.UI_viewer_start()

    def Qt_submit_click(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            self.Qt_window,
            "Generate Report",
            self.reportpath,
            "*.smpl"
        )
        if filename:
            self.UI_submit(str(filename))

    def Qt_state_reset_click(self):
        self.UI_state_reset()

    def Qt_state_load_click(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            self.Qt_window,
            "Import Setup from Report",
            self.reportpath,
            "*.smpl"
        )
        if filename:
            self.UI_state_import(str(filename))

    def Qt_sampler_change(self):
        if self.Qt_setting:
            return
        self.UI_sampler_change(str(self.Qt_sampler.currentText()))

    def Qt_sampler_about_show(self):
        self.Qt_sampler_aboutD.show()

    def Qt_nt_change(self):
        if self.Qt_setting:
            return
        self.UI_nt_change(int(self.Qt_nt.currentText()))

    def Qt_userange_toggle(self, checked):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        value = rangename if checked else None
        if rangename in self.rangetypes["outer"]:
            self.UI_userange_change("outer", value)
        else:
            self.UI_userange_change("inner", value)

    def Qt_option_toggle(self, checked):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        optionname = sender.optionname
        self.UI_option_change(optionname, checked)

    def Qt_showarg_toggle(self, checked):
        if self.Qt_setting:
            return
        argtype = self.Qt_app.sender().argtype
        self.UI_showargs_change(argtype, checked)

    def Qt_counters_close(self, event):
        if self.Qt_setting:
            return
        self.UI_option_change("papi", False)

    def Qt_counter_change(self):
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

    def Qt_header_change(self):
        text = str(self.Qt_header.toPlainText())
        height = self.Qt_header.fontMetrics().lineSpacing()
        self.Qt_header.setFixedHeight(height * (text.count("\n") + 2))
        if self.Qt_setting:
            return
        self.UI_header_change(text)

    def Qt_header_close(self, event):
        if self.Qt_setting:
            return
        self.UI_option_change("header", False)

    def Qt_rangevar_change(self):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        value = str(sender.text())
        self.UI_rangevar_change(rangename, value)

    def Qt_range_change(self):
        if self.Qt_setting:
            return
        sender = self.Qt_app.sender()
        rangename = sender.rangename
        value = str(sender.text())
        if rangename == "reps":
            self.UI_nrep_change(value)
        else:
            self.UI_range_change(rangename, value)

    def Qt_call_add_click(self):
        self.UI_call_add_click()

    def Qt_calls_reorder(self):
        order = []
        for i in range(self.Qt_calls.count()):
            Qcall = self.Qt_calls.item(i)
            order.append(Qcall.callid)
            Qcall.callid = i
        self.UI_calls_reorder(order)

    def Qt_calls_focusout(self, event):
        for callid in range(self.Qt_calls.count()):
            self.Qt_calls.setItemSelected(self.Qt_calls.item(callid), False)

    def Qt_jobprogress_click(self):
        sender = self.Qt_app.sender()
        jobid = sender.jobid
        job = self.jobprogress[jobid]
        if job["progress"] <= job["progressend"]:
            self.UI_jobkill(jobid)
        else:
            self.UI_jobview(jobid)


def main():
    loadstate = "--reset" not in sys.argv[1:]
    GUI_Qt(loadstate=loadstate).start()


if __name__ == "__main__":
    main()
