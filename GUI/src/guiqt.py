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
        self.app = app if app else QtGui.QApplication(sys.argv)
        self.Qt_setting = False
        self.Qt_initialized = False
        GUI.__init__(self, loadstate)

    def state_init(self, load=True):
        if load:
            settings = QtCore.QSettings("HPAC", "Sampler")
            self.Qt_setting = True
            self.Qt_window.restoreGeometry(
                settings.value("geometry").toByteArray()
            )
            self.Qt_window.restoreState(
                settings.value("windowState").toByteArray()
            )
            self.Qt_setting = False
            try:
                self.state_fromstring(str(
                    settings.value("appState").toString()
                ))
            except:
                self.state_reset()
        else:
            self.state_reset()

    def UI_init(self):
        self.Qt_setting = True
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

            # file > quite
            quit = QtGui.QAction("Quit", window)
            fileM.addAction(quit)
            quit.triggered.connect(self.Qt_submit_click)
            quit.setMenuRole(QtGui.QAction.QuitRole)

            # ranges
            rangesM = menu.addMenu("Ranges")

            # usentrange
            self.Qt_usentrange = QtGui.QAction("#threads range", window)
            rangesM.addAction(self.Qt_usentrange)
            self.Qt_usentrange.setCheckable(True)
            self.Qt_usentrange.toggled.connect(self.Qt_usentrange_toggle)

            # userange
            self.Qt_userange = QtGui.QAction("for each range", window)
            rangesM.addAction(self.Qt_userange)
            self.Qt_userange.setCheckable(True)
            self.Qt_userange.toggled.connect(self.Qt_userange_toggle)

            # usesumrange
            self.Qt_usesumrange = QtGui.QAction("sum over sumrange", window)
            rangesM.addAction(self.Qt_usesumrange)
            self.Qt_usesumrange.setCheckable(True)
            self.Qt_usesumrange.toggled.connect(self.Qt_usesumrange_toggle)

            # options
            optionsM = menu.addMenu("Options")

            # options > usepapi
            self.Qt_usepapi = QtGui.QAction("use papi", window)
            optionsM.addAction(self.Qt_usepapi)
            self.Qt_usepapi.setCheckable(True)
            self.Qt_usepapi.toggled.connect(self.Qt_usepapi_toggle)

            # options > header
            self.Qt_useheader = QtGui.QAction("script header", window)
            optionsM.addAction(self.Qt_useheader)
            self.Qt_useheader.setCheckable(True)
            self.Qt_useheader.toggled.connect(self.Qt_useheader_toggle)

            # options > usevary
            self.Qt_usevary = QtGui.QAction("vary matrices", window)
            optionsM.addAction(self.Qt_usevary)
            self.Qt_usevary.setCheckable(True)
            self.Qt_usevary.toggled.connect(self.Qt_usevary_toggle)

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

            # sampler
            self.Qt_sampler = QtGui.QComboBox()
            samplerT.addWidget(self.Qt_sampler)
            self.Qt_sampler.addItems(sorted(self.samplers.keys()))
            self.Qt_sampler.currentIndexChanged.connect(self.Qt_sampler_change)

            # nt
            self.Qt_ntlabel = QtGui.QLabel("#threads:")
            samplerT.addWidget(self.Qt_ntlabel)
            self.Qt_nt = QtGui.QComboBox()
            samplerT.addWidget(self.Qt_nt)
            self.Qt_nt.currentIndexChanged.connect(self.Qt_nt_change)

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
            icon = self.app.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)
            self.Qt_submit = QtGui.QAction(icon, "Run", window)
            samplerT.addAction(self.Qt_submit)
            self.Qt_submit.triggered.connect(self.Qt_submit_click)

        def create_ranges():
            rangesD = QtGui.QDockWidget("Ranges")
            window.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                                 rangesD)
            rangesD.setObjectName("Ranges")
            rangesD.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar)
            rangesW = QtGui.QWidget()
            rangesD.setWidget(rangesW)
            rangesW.setSizePolicy(
                QtGui.QSizePolicy.Minimum,
                QtGui.QSizePolicy.Fixed,
            )
            rangesL = QtGui.QVBoxLayout()
            rangesW.setLayout(rangesL)
            margins = list(rangesL.getContentsMargins())
            margins[1] = margins[3] = 0
            rangesL.setContentsMargins(*margins)
            rangesL.setSpacing(0)

            # ntrange
            self.Qt_ntrangeW = QtGui.QWidget()
            rangesL.addWidget(self.Qt_ntrangeW)
            ntrangeL = QtGui.QHBoxLayout()
            self.Qt_ntrangeW.setLayout(ntrangeL)
            ntrangeL.setContentsMargins(0, 12, 12, 4)

            # ntrange > "for #threads nt ="
            ntrangeL.addWidget(QtGui.QLabel("for nt ="))

            # ntrange > ntrange
            self.Qt_ntrange = QtGui.QLineEdit()
            ntrangeL.addWidget(self.Qt_ntrange)
            self.Qt_ntrange.textChanged.connect(self.Qt_ntrange_change)
            regexp = QtCore.QRegExp("(?:\d+)?:(?:(?:\d+)?:)?(\d+)?")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_ntrange.setValidator(validator)

            # ntrange > "(#threads)"
            ntrangeL.addWidget(QtGui.QLabel("(#threads)"))

            # ntrange
            ntrangeL.addStretch(1)

            # range
            self.Qt_rangeW = QtGui.QWidget()
            rangesL.addWidget(self.Qt_rangeW)
            rangeL = QtGui.QHBoxLayout()
            self.Qt_rangeW.setLayout(rangeL)
            rangeL.setContentsMargins(0, 12, 12, 4)

            # range > "for"
            rangeL.addWidget(QtGui.QLabel("for"))

            # range > rangevar
            self.Qt_rangevar = QtGui.QLineEdit()
            rangeL.addWidget(self.Qt_rangevar)
            self.Qt_rangevar.textChanged.connect(self.Qt_rangevar_change)
            self.Qt_rangevar.setFixedWidth(32)
            regexp = QtCore.QRegExp("[a-zA-Z]+")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_rangevar.setValidator(validator)

            # range > "="
            rangeL.addWidget(QtGui.QLabel("="))

            # range > range
            self.Qt_range = QtGui.QLineEdit()
            rangeL.addWidget(self.Qt_range)
            self.Qt_range.textChanged.connect(self.Qt_range_change)
            regexp = QtCore.QRegExp("(?:-?\d+)?:(?:(?:-?\d+)?:)?(-?\d+)?")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_range.setValidator(validator)

            # range
            rangeL.addStretch(1)

            # nrep
            nrepW = QtGui.QWidget()
            rangesL.addWidget(nrepW)
            nrepL = QtGui.QHBoxLayout()
            nrepW.setLayout(nrepL)
            nrepL.setContentsMargins(16, 0, 12, 4)

            # nrep > "repeat"
            nrepL.addWidget(QtGui.QLabel("repeat"))

            # nrep > nrep
            self.Qt_nrep = QtGui.QLineEdit()
            nrepL.addWidget(self.Qt_nrep)
            self.Qt_nrep.textChanged.connect(self.Qt_nrep_change)
            self.Qt_nrep.setFixedWidth(32)
            regexp = QtCore.QRegExp("[1-9][0-9]*")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_nrep.setValidator(validator)

            # nrep > "times"
            nrepL.addWidget(QtGui.QLabel("times"))

            # range
            nrepL.addStretch(1)

            # sumrange
            self.Qt_sumrangeW = QtGui.QWidget()
            rangesL.addWidget(self.Qt_sumrangeW)
            sumrangeL = QtGui.QHBoxLayout()
            self.Qt_sumrangeW.setLayout(sumrangeL)
            sumrangeL.setContentsMargins(32, 0, 12, 0)

            # sumrange > "for"
            sumrangeL.addWidget(QtGui.QLabel("sum over"))

            # sumrange > sumrangevar
            self.Qt_sumrangevar = QtGui.QLineEdit()
            sumrangeL.addWidget(self.Qt_sumrangevar)
            self.Qt_sumrangevar.textChanged.connect(self.Qt_sumrangevar_change)
            self.Qt_sumrangevar.setFixedWidth(32)
            regexp = QtCore.QRegExp("[a-zA-Z]+")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_sumrangevar.setValidator(validator)

            # sumrange > "="
            sumrangeL.addWidget(QtGui.QLabel("="))

            # sumrange > sumrange
            self.Qt_sumrange = QtGui.QLineEdit()
            sumrangeL.addWidget(self.Qt_sumrange)
            self.Qt_sumrange.textChanged.connect(self.Qt_sumrange_change)
            regexp = QtCore.QRegExp("(?:.*)?:(?:(?:.*)?:)?(.*)?")
            validator = QtGui.QRegExpValidator(regexp, self.app)
            self.Qt_sumrange.setValidator(validator)

            # sumrange
            sumrangeL.addStretch(1)

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
            self.Qt_headerD.visibilityChanged.connect(
                self.Qt_header_visibility_change
            )
            self.Qt_header = QtGui.QPlainTextEdit()
            self.Qt_headerD.setWidget(self.Qt_header)
            self.Qt_header.textChanged.connect(self.Qt_header_change)

        def create_counters():
            self.Qt_countersD = QtGui.QDockWidget("PAPI Counters")
            window.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                                 self.Qt_countersD)
            self.Qt_headerD.visibilityChanged.connect(
                self.Qt_counters_visibility_change
            )
            self.Qt_countersD.setObjectName("PAPI Coutners")
            self.Qt_counters = QtGui.QWidget()
            self.Qt_countersD.setWidget(self.Qt_counters)
            self.Qt_counters.setLayout(QtGui.QVBoxLayout())
            self.Qt_counters.setSizePolicy(
                QtGui.QSizePolicy.Minimum,
                QtGui.QSizePolicy.Fixed,
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
            self.Qt_Qcalls = []
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
            self.app.setStyleSheet("""
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

            palette = self.app.palette()
            dark = palette.text().color()
            darka = palette.text().color()
            darka.setAlpha(127)
            # pens and brushes (for dataargs)
            self.Qt_pens = {
                None: QtGui.QColor(0, 0, 255, 0),
                "maxfront": darka,
                "maxback": QtGui.QPen(darka, 0, style=QtCore.Qt.DashLine),
                "minfront": dark,
                "minback": QtGui.QPen(dark, 0, style=QtCore.Qt.DashLine),
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
        create_submit()
        create_ranges()
        create_header()
        create_counters()
        create_calls()
        create_jobprogress()
        create_statusbar()
        create_style()
        window.show()

        self.Qt_viewer = None

        self.Qt_setting = False
        self.Qt_initialized = True

    def UI_start(self):
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(self.app.exec_())

    # dialogs
    def UI_alert(self, *args, **kwargs):
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_setstatus(self, *args):
        if self.Qt_initialized:
            self.Qt_statusbar.showMessage(" ".join(map(str, args)))

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
        self.Qt_setting = True
        self.Qt_sampler.setCurrentIndex(
            self.Qt_sampler.findText(self.samplername)
        )
        self.Qt_setting = False

    def UI_sampler_about_set(self):
        self.Qt_sampler_about.setText(self.sampler_about_str())

    def UI_nt_setmax(self):
        self.Qt_setting = True
        self.Qt_nt.clear()
        self.Qt_nt.addItems(map(str, range(1, self.sampler["nt_max"] + 1)))
        self.Qt_setting = False

    def UI_nt_set(self):
        self.Qt_setting = True
        self.Qt_nt.setCurrentIndex(self.nt - 1)
        self.Qt_setting = False

    def UI_userange_setenabled(self):
        self.Qt_usentrange.setEnabled(not self.userange)
        self.Qt_userange.setEnabled(not self.usentrange)
        self.Qt_ntlabel.setVisible(not self.usentrange)
        self.Qt_nt.setVisible(not self.usentrange)

    def UI_usentrange_set(self):
        self.Qt_setting = True
        self.Qt_usentrange.setChecked(self.usentrange)
        self.Qt_setting = False

    def UI_usentrange_apply(self):
        self.Qt_ntrangeW.setVisible(self.usentrange)

    def UI_userange_set(self):
        self.Qt_setting = True
        self.Qt_userange.setChecked(self.userange)
        self.Qt_setting = False

    def UI_userange_apply(self):
        self.Qt_rangeW.setVisible(self.userange)

    def UI_usesumrange_set(self):
        self.Qt_setting = True
        self.Qt_usesumrange.setChecked(self.usesumrange)
        self.Qt_setting = False

    def UI_usesumrange_apply(self):
        self.Qt_sumrangeW.setVisible(self.usesumrange)

    def UI_usepapi_setenabled(self):
        self.Qt_usepapi.setEnabled(self.sampler["papi_counters_max"] > 0)

    def UI_usepapi_set(self):
        self.Qt_setting = True
        self.Qt_usepapi.setChecked(self.usepapi)
        self.Qt_setting = False

    def UI_usevary_set(self):
        self.Qt_setting = True
        self.Qt_usevary.setChecked(self.usevary)
        self.Qt_setting = False

    def UI_showargs_set(self, name=None):
        if name is None:
            for name in self.Qt_showargs:
                self.UI_showargs_set(name)
            return
        self.Qt_setting = True
        self.Qt_showargs[name].setChecked(self.showargs[name])
        self.Qt_setting = False

    def UI_counters_setvisible(self):
        self.Qt_setting = True
        self.Qt_countersD.setVisible(self.usepapi)
        self.Qt_setting = False

    def UI_useheader_set(self):
        self.Qt_setting = True
        self.Qt_useheader.setChecked(self.useheader)
        self.Qt_setting = False

    def UI_header_set(self):
        self.Qt_setting = True
        self.Qt_header.setPlainText(self.header)
        self.Qt_setting = False

    def UI_header_setvisible(self):
        self.Qt_setting = True
        self.Qt_headerD.setVisible(self.useheader)
        self.Qt_setting = False

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
        self.Qt_setting = True
        for Qcounter, countername in zip(self.Qt_Qcounters, self.counters):
            index = Qcounter.findData(QtCore.QVariant(countername))
            Qcounter.setCurrentIndex(index)
            tip = ""
            if countername:
                tip = countername + "\n" + papi.events[countername]["long"]
            Qcounter.setToolTip(tip)
        self.Qt_setting = False

    def UI_ntrange_set(self):
        self.Qt_setting = True
        lower, step, upper = self.ntrange
        text = ""
        if lower is not None:
            text += str(lower)
        if step != 1:
            text += ":" + str(step)
        text += ":"
        if upper is not None:
            text += str(upper)
        self.Qt_ntrange.setText(text)
        self.Qt_setting = False

    def UI_rangevar_set(self):
        self.Qt_setting = True
        self.Qt_rangevar.setText(self.rangevar)
        self.Qt_setting = False

    def UI_range_set(self):
        self.Qt_setting = True
        lower, step, upper = self.range
        text = ""
        if lower is not None:
            text += str(lower)
        if step != 1:
            text += ":" + str(step)
        text += ":"
        if upper is not None:
            text += str(upper)
        self.Qt_range.setText(text)
        self.Qt_setting = False

    def UI_nrep_set(self):
        self.Qt_setting = True
        text = str(self.nrep) if self.nrep else ""
        self.Qt_nrep.setText(text)
        self.Qt_setting = False

    def UI_sumrangevar_set(self):
        self.Qt_setting = True
        self.Qt_sumrangevar.setText(self.sumrangevar)
        self.Qt_setting = False

    def UI_sumrange_set(self):
        self.Qt_setting = True
        lower, step, upper = map(str, self.sumrange)
        text = ""
        if lower is not None:
            text += str(lower)
        if step != 1:
            text += ":" + str(step)
        text += ":"
        if upper is not None:
            text += str(upper)
        self.Qt_sumrange.setText(text)
        self.Qt_setting = False

    def UI_calls_init(self):
        self.Qt_setting = True
        # delete old
        self.Qt_calls.clear()
        self.Qt_Qcalls = []
        # add new
        for callid in range(len(self.calls)):
            self.UI_call_add(callid)
        self.Qt_setting = False

    def UI_call_add(self, callid=None):
        if callid is None:
            callid = len(self.calls) - 1
        Qcall = QCall(self, callid)
        self.Qt_calls.addItem(Qcall)
        self.Qt_calls.setItemWidget(Qcall, Qcall.widget)
        self.Qt_Qcalls.append(Qcall)
        Qcall.args_set()

    def UI_call_set(self, callid, fromargid=None):
        self.Qt_setting = True
        self.Qt_Qcalls[callid].args_set(fromargid)
        self.Qt_setting = False

    def UI_calls_set(self, fromcallid=None, fromargid=None):
        self.Qt_setting = True
        for callid, Qcall in enumerate(self.Qt_Qcalls):
            Qcall.args_set(fromargid if fromcallid == callid else None)
        self.Qt_setting = False

    def UI_data_viz(self):
        self.Qt_setting = True
        for Qcall in self.Qt_Qcalls:
            Qcall.data_viz()
        self.Qt_setting = False

    def UI_showargs_apply(self):
        for Qcall in self.Qt_Qcalls:
            Qcall.showargs_apply()

    def UI_usevary_apply(self):
        for Qcall in self.Qt_Qcalls:
            Qcall.usevary_apply()

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
                name = os.path.basename(job["filename"])[:-5]
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
            if job["progress"] < 0:
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

    def UI_viewer_load(self, filename):
        if self.Qt_viewer is None:
            from viewerqtmpl import Viewer_Qt_MPL
            self.Qt_viewer = Viewer_Qt_MPL(self.app)
        self.Qt_viewer.UI_load_report(filename)
        self.Qt_viewer.Qt_window.show()

    # event handlers
    def UI_window_close(self):
        settings = QtCore.QSettings("HPAC", "Sampler")
        settings.setValue("geometry", self.Qt_window.saveGeometry())
        settings.setValue("windowState", self.Qt_window.saveState())
        settings.setValue("appState",
                          QtCore.QVariant(repr(self.state_toflat())))

    def Qt_window_close(self, event):
        self.UI_window_close()

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

    def Qt_usentrange_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_usentrange_change(checked)

    def Qt_userange_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_userange_change(checked)

    def Qt_usesumrange_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_usesumrange_change(checked)

    def Qt_usepapi_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_usepapi_change(checked)

    def Qt_useheader_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_useheader_change(checked)

    def Qt_usevary_toggle(self, checked):
        if self.Qt_setting:
            return
        self.UI_usevary_change(checked)

    def Qt_showarg_toggle(self, checked):
        if self.Qt_setting:
            return
        argtype = self.app.sender().argtype
        self.UI_showargs_change(argtype, checked)

    def Qt_counters_visibility_change(self, visible):
        if self.Qt_setting:
            return
        if not visible:
            self.UI_usepapi_change(False)
            self.UI_usepapi_set()

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

    def Qt_header_visibility_change(self, visible):
        if self.Qt_setting:
            return
        if not visible:
            self.UI_useheader_change(False)
            self.UI_useheader_set()

    def Qt_ntrange_change(self):
        if self.Qt_setting:
            return
        parts = str(self.Qt_ntrange.text()).split(":")
        lower = int(parts[0]) if len(parts) >= 1 and parts[0] else None
        step = int(parts[1]) if len(parts) == 3 and parts[1] else 1
        upper = int(parts[-1]) if len(parts) >= 2 and parts[-1] else None
        self.UI_ntrange_change((lower, step, upper))

    def Qt_rangevar_change(self):
        if self.Qt_setting:
            return
        self.UI_rangevar_change(str(self.Qt_rangevar.text()))

    def Qt_range_change(self):
        if self.Qt_setting:
            return
        parts = str(self.Qt_range.text()).split(":")
        lower = int(parts[0]) if len(parts) >= 1 and parts[0] else None
        step = int(parts[1]) if len(parts) == 3 and parts[1] else 1
        upper = int(parts[-1]) if len(parts) >= 2 and parts[-1] else None
        self.UI_range_change((lower, step, upper))

    def Qt_nrep_change(self):
        if self.Qt_setting:
            return
        text = str(self.Qt_nrep.text())
        self.UI_nrep_change(int(text) if text else None)

    def Qt_sumrangevar_change(self):
        if self.Qt_setting:
            return
        self.UI_sumrangevar_change(str(self.Qt_sumrangevar.text()))

    def Qt_sumrange_change(self):
        if self.Qt_setting:
            return
        parts = str(self.Qt_sumrange.text()).split(":")
        lower = parts[0] if len(parts) >= 1 else None
        step = parts[1] if len(parts) == 3 else 1
        upper = parts[-1] if len(parts) >= 2 else None
        self.UI_sumrange_change((lower, step, upper))

    def Qt_call_add_click(self):
        self.UI_call_add_click()

    def Qt_calls_reorder(self):
        order = [self.Qt_calls.item(i).callid
                 for i in range(self.Qt_calls.count())]
        self.UI_calls_reorder(order)
        self.Qt_Qcalls = [self.Qt_Qcalls[i] for i in order]

    def Qt_calls_focusout(self, event):
        for Qcall in self.Qt_Qcalls:
            self.Qt_calls.setItemSelected(Qcall, False)

    def Qt_jobprogress_click(self):
        sender = self.app.sender()
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
