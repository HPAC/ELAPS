#!/usr/bin/env python
"""GUI for Experiments."""
from __future__ import division, print_function

import elapsio
from experiment import Experiment
import symbolic
import signature

from qt import QCall

import sys
import os
import string
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot


class PlayMat(object):

    """GUI for Experiment."""

    datascale = 100
    defaultdim = 1000

    def __init__(self, app=None, load=None, reset=False):
        """Initilialize the PlayMat."""
        if app:
            self.Qapp = app
        else:
            self.Qapp = QtGui.QApplication(sys.argv)
            self.Qapp.viewer = None
        self.Qapp.playmat = self
        self.backends = elapsio.load_all_backends()
        self.samplers = elapsio.load_all_samplers()
        self.docs = {}
        self.sigs = {}
        self.jobs = {}
        self.hideargs = set([signature.Ld, signature.Inc, signature.Work,
                             signature.Lwork, signature.Info])

        self.UI_init()
        if not reset:
            try:
                self.UI_settings_load()
            except:
                pass

        # set experiment
        self.experiment = None
        if load:
            try:
                self.experiment_load(sys.argv[1])
            except:
                self.alert("ERROR: Can't load %r" % sys.argv[1])
        if not self.experiment and not reset:
            try:
                self.experiment_qt_load()
            except:
                pass
        if not self.experiment:
            self.experiment_load(
                os.path.join(elapsio.setuppath, "default.ees")
            )
        self.experiment_back = Experiment(self.experiment)

        self.experiment.update_data()

        self.UI_setall()

    def UI_init(self):
        """Initialize all GUI elements."""
        self.UI_setting = 1

        # window
        window = self.UI_window = QtGui.QMainWindow(
            windowTitle="ELAPS:PlayMat",
            unifiedTitleAndToolBarOnMac=True
        )
        window.closeEvent = self.on_window_close
        window.setCorner(QtCore.Qt.TopRightCorner,
                         QtCore.Qt.RightDockWidgetArea)

        # DEBUG: print experiment
        loadreport = QtGui.QShortcut(
            QtGui.QKeySequence.Print, window, lambda: print(self.experiment)
        )

        def create_menus():
            """Create all menus."""
            menu = window.menuBar()

            # file
            fileM = menu.addMenu("File")

            # file > submit
            self.UI_submitA = QtGui.QAction(
                "Run", window,
                shortcut=QtGui.QKeySequence("Ctrl+R"), triggered=self.on_submit
            )
            fileM.addAction(self.UI_submitA)

            # file
            fileM.addSeparator()

            # file > reset
            fileM.addAction(QtGui.QAction(
                "Reset Experiment", window, triggered=self.on_experiment_reset
            ))

            # file > load
            load = QtGui.QAction(
                "Load Experiment ...", window,
                shortcut=QtGui.QKeySequence.Open,
                triggered=self.on_experiment_load
            )
            fileM.addAction(load)

            # load report shortcut
            loadreport = QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+O"),
                window, self.on_experiment_load_report
            )

            # fie > save
            fileM.addAction(QtGui.QAction(
                "Save Experiment ...", window,
                shortcut=QtGui.QKeySequence.Save,
                triggered=self.on_experiment_save
            ))

            # file
            fileM.addSeparator()

            fileM.addAction(QtGui.QAction(
                "Start Viewer", window, triggered=self.on_viewer_start
            ))

            # view
            self.UI_viewM = menu.addMenu("View")

            # view > hideargs
            self.UI_hideargs = []
            for desc, classes in (
                ("hide flags", (signature.Flag,)),
                ("hide scalars", (signature.Scalar,)),
                ("hide leading dimensions", (signature.Ld, signature.Inc)),
                ("hide work spaces", (signature.Work, signature.Lwork)),
                ("hide infos", (signature.Info,))
            ):
                action = QtGui.QAction(
                    desc, window,
                    checkable=True, toggled=self.on_hideargs_toggle
                )
                action.classes = set(classes)
                self.UI_viewM.addAction(action)
                self.UI_hideargs.append((action, set(classes)))

        def create_sampler():
            """Create the sampler Toolbar."""
            self.UI_sampler = QtGui.QComboBox()
            self.UI_sampler.addItems(sorted(self.samplers.keys()))
            self.UI_sampler.currentIndexChanged[str].connect(
                self.on_sampler_change
            )

            samplerT = window.addToolBar("Sampler")
            samplerT.pyqtConfigure(movable=True, objectName="Sampler")
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            samplerT.addWidget(self.UI_sampler)

        def create_nthreads():
            """Create the #threads toolbar."""
            self.UI_nthreads = QtGui.QComboBox()
            self.UI_nthreads.currentIndexChanged[str].connect(
                self.on_nthreads_change
            )

            nthreadsT = window.addToolBar("#threads")
            nthreadsT.pyqtConfigure(movable=True, objectName="#threads")
            nthreadsT.addWidget(QtGui.QLabel("#threads:"))
            nthreadsT.addWidget(self.UI_nthreads)

        def create_submit():
            """Create the submit toolbar."""
            samplerT = window.addToolBar("Submit")
            samplerT.pyqtConfigure(movable=False, objectName="Submit")

            # spacer
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
            samplerT.addWidget(spacer)

            # submit
            self.UI_submit = QtGui.QAction(window.style().standardIcon(
                QtGui.QStyle.SP_DialogOkButton
            ), "Run", window, triggered=self.on_submit)
            samplerT.addAction(self.UI_submit)

        def create_ranges():
            """Create the ranges dock widget."""
            # checkboxes
            self.UI_userange = QtGui.QCheckBox(
                " ", toggled=self.on_userange_toggle
            )

            self.UI_usesumrange = QtGui.QCheckBox(
                " ", toggled=self.on_usesumrange_toggle
            )

            self.UI_calls_parallel = QtGui.QCheckBox(
                " ", toggled=self.on_calls_parallel_toggle
            )

            # range
            self.UI_rangevar = QtGui.QLineEdit(
                textChanged=self.on_rangevar_change
            )
            self.UI_rangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_rangevar
            ))
            self.UI_rangevar.setFixedWidth(32)
            self.UI_rangevals = QtGui.QLineEdit(
                textChanged=self.on_rangevals_change
            )

            rangeL = QtGui.QHBoxLayout(spacing=0)
            rangeL.setContentsMargins(0, 0, 0, 0)
            rangeL.addWidget(QtGui.QLabel("for "))
            rangeL.addWidget(self.UI_rangevar)
            rangeL.addWidget(QtGui.QLabel(" = "))
            rangeL.addWidget(self.UI_rangevals)
            rangeL.addWidget(QtGui.QLabel(":"))
            rangeL.addStretch(1)
            self.UI_rangeW = QtGui.QWidget()
            self.UI_rangeW.setLayout(rangeL)

            # reps
            self.UI_nreps = QtGui.QLineEdit(textChanged=self.on_nreps_change)
            self.UI_nreps.setValidator(QtGui.QIntValidator(bottom=1))
            self.UI_nreps.setFixedWidth(32)

            nrepsL = QtGui.QHBoxLayout(spacing=0)
            nrepsL.setContentsMargins(16, 4, 0, 0)
            nrepsL.addWidget(QtGui.QLabel("repeat "))
            nrepsL.addWidget(self.UI_nreps)
            nrepsL.addWidget(QtGui.QLabel(" times:"))
            nrepsL.addStretch(1)
            self.UI_nrepsW = QtGui.QWidget()
            self.UI_nrepsW.setLayout(nrepsL)

            # sumrange
            self.UI_sumrange_parallel = QtGui.QComboBox()
            self.UI_sumrange_parallel.addItems(["sum over", "#omp for"])
            self.UI_sumrange_parallel.currentIndexChanged[int].connect(
                self.on_sumrange_parallel_change
            )
            self.UI_sumrangevar = QtGui.QLineEdit(
                textChanged=self.on_sumrangevar_change
            )
            self.UI_sumrangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_sumrangevar
            ))
            self.UI_sumrangevar.setFixedWidth(32)
            self.UI_sumrangevals = QtGui.QLineEdit(
                textChanged=self.on_sumrangevals_change
            )

            sumrangeL = QtGui.QHBoxLayout(spacing=0)
            sumrangeL.setContentsMargins(32, 0, 0, 0)
            sumrangeL.addWidget(self.UI_sumrange_parallel)
            sumrangeL.addWidget(QtGui.QLabel(" "))
            sumrangeL.addWidget(self.UI_sumrangevar)
            sumrangeL.addWidget(QtGui.QLabel(" = "))
            sumrangeL.addWidget(self.UI_sumrangevals)
            sumrangeL.addWidget(QtGui.QLabel(":"))
            sumrangeL.addStretch(1)
            self.UI_sumrangeW = QtGui.QWidget()
            self.UI_sumrangeW.setLayout(sumrangeL)

            # calls_parallel
            calls_parallelL = QtGui.QHBoxLayout()
            calls_parallelL.setContentsMargins(48, 0, 0, 0)
            calls_parallelL.addWidget(QtGui.QLabel("in parallel:"))
            calls_parallelL.addStretch(1)
            self.UI_calls_parallelW = QtGui.QWidget()
            self.UI_calls_parallelW.setLayout(calls_parallelL)

            rangesL = QtGui.QGridLayout(spacing=0)
            rangesL.addWidget(self.UI_userange, 0, 0)
            rangesL.addWidget(self.UI_rangeW, 0, 1)
            rangesL.addWidget(self.UI_nrepsW, 1, 1)
            rangesL.addWidget(self.UI_usesumrange, 2, 0)
            rangesL.addWidget(self.UI_sumrangeW, 2, 1)
            rangesL.addWidget(self.UI_calls_parallel, 3, 0)
            rangesL.addWidget(self.UI_calls_parallelW, 3, 1)

            rangesW = QtGui.QWidget()
            rangesW.setLayout(rangesL)

            rangesD = QtGui.QDockWidget(
                "Ranges", objectName="Ranges",
                features=QtGui.QDockWidget.DockWidgetVerticalTitleBar,
            )
            rangesD.setWidget(rangesW)

            window.addDockWidget(QtCore.Qt.TopDockWidgetArea, rangesD)

        def create_calls():
            """Create the calls list and add button (central widget)."""
            self.UI_calls = QtGui.QListWidget(
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                dragDropMode=QtGui.QAbstractItemView.InternalMove,
                customContextMenuRequested=self.on_calls_rightclick
            )
            self.UI_calls.model().layoutChanged.connect(self.on_calls_reorder)
            self.UI_calls.focusOutEvent = self.on_calls_focusout

            window.setCentralWidget(self.UI_calls)

            # context menus
            self.UI_call_contextmenu = QtGui.QMenu()
            self.UI_calls_contextmenu = QtGui.QMenu()

            # add
            add = QtGui.QAction("Add call", window, triggered=self.on_call_add)
            self.UI_call_contextmenu.addAction(add)
            self.UI_calls_contextmenu.addAction(add)

            # remove
            self.UI_call_contextmenu.addAction(QtGui.QAction(
                "Remove call", window, triggered=self.on_call_remove
            ))

            # clone
            self.UI_call_contextmenu.addAction(QtGui.QAction(
                "Clone call", window, triggered=self.on_call_clone
            ))

            self.UI_call_contextmenu.addSeparator()
            self.UI_calls_contextmenu.addSeparator()

            self.UI_call_contextmenu.addMenu(self.UI_viewM)
            self.UI_calls_contextmenu.addMenu(self.UI_viewM)

        def create_jobprogress():
            """Create the job pgoress dock widget."""
            jobprogressL = QtGui.QGridLayout()

            jobprogress = QtGui.QWidget()
            jobprogress.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                      QtGui.QSizePolicy.Fixed)
            jobprogress.setLayout(jobprogressL)

            self.UI_jobprogressD = QtGui.QDockWidget(
                "Job Progress", objectName="Job Progress"
            )
            self.UI_jobprogressD.setWidget(jobprogress)

            window.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                                 self.UI_jobprogressD)
            self.UI_jobprogressD.hide()

            self.UI_jobprogress_jobs = {}

            # timer
            self.jobprogress_timer = QtCore.QTimer(
                interval=1000,
                timeout=self.on_jobprogress_timer
            )

        def create_statusbar():
            """Create the staus bar."""
            window.statusBar()

        def create_style():
            """Set style options."""
            # stylesheet
            window.setStyleSheet("""
                QLineEdit[invalid="true"],
                *[invalid="true"] QLineEdit {
                    background: #FFDDDD;
                }
                QLabel:disabled,
                QLineEdit:disabled {
                    color: #888888;
                }
            """)

            palette = self.Qapp.palette()
            dark = palette.text().color()
            darka = palette.text().color()
            darka.setAlpha(63)
            # pens and brushes (for dataargs)
            self.pens = {
                None: QtGui.QColor(0, 0, 255, 0),
                "maxfront": darka,
                "maxback": QtGui.QPen(darka, 0, QtCore.Qt.DashLine),
                "minfront": dark,
                "minback": QtGui.QPen(dark, 0, QtCore.Qt.DashLine)
            }
            windowcolor = palette.window().color()
            windowcoloralpha = palette.window().color()
            windowcoloralpha.setAlpha(63)
            self.brushes = {
                "max": windowcoloralpha,
                "min": windowcolor
            }

        create_menus()
        create_sampler()
        create_nthreads()
        create_submit()
        create_ranges()
        create_calls()
        create_jobprogress()
        create_statusbar()
        create_style()

        window.show()

        self.UI_setting -= 1
        self.UI_initialized = True

    def UI_settings_load(self):
        """Load Qt settings."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        self.hideargs = eval(settings.value("hideargs", type=str))
        self.UI_setting += 1
        self.UI_window.restoreGeometry(
            settings.value("geometry").toByteArray()
        )
        self.UI_window.restoreState(
            settings.value("windowState").toByteArray()
        )
        self.UI_setting -= 1

    def start(self):
        """Start the Mat (enter the main loop)."""
        import signal
        signal.signal(signal.SIGINT, self.on_console_quit)

        # make sure python handles signals every 500ms
        timer = QtCore.QTimer(timeout=lambda: None)
        timer.start(500)

        sys.exit(self.Qapp.exec_())

    # utility
    @staticmethod
    def log(*args):
        """Log a message to stdout."""
        print(*args)

    @staticmethod
    def alert(*args):
        """Log a message to stderr."""
        print("\033[31m" + " ".join(map(str, args)) + "\033[0m",
              file=sys.stderr)

    # experiment routines
    def experiment_qt_load(self):
        """Load Experiment from Qt setting."""
        ex = elapsio.load_experiment_string(str(
            QtCore.QSettings("HPAC", "ELAPS:PlayMat").value("Experiment",
                                                            type=str)
        ))
        if ex.sampler is None or ex.sampler["name"] not in self.samplers:
            ex.sampler = self.samplers[min(self.samplers)]
        else:
            ex.sampler = self.samplers[ex.sampler["name"]]
        self.experiment = ex
        self.log("Loaded last Experiment")

    def experiment_load(self, filename):
        """Load Experiment from a file."""
        ex = elapsio.load_experiment(filename)
        if ex.sampler is None or ex.sampler["name"] not in self.samplers:
            ex.sampler = self.samplers[min(self.samplers)]
        else:
            ex.sampler = self.samplers[ex.sampler["name"]]
        self.experiment = ex
        self.log("Loaded Experiment from %r." % os.path.relpath(filename))

    def experiment_write(self, filename):
        """Write Experiment to a file."""
        elapsio.wrte_experiment(self.experiment, filename)
        self.log("Written Experiment to %r." % os.path.relpath(filename))

    def experiment_infer_update(self, callid=None):
        """Infer Ld and Lwork (if not showing) and update_data()."""
        ex = self.experiment
        if signature.Ld in self.hideargs:
            ex.infer_lds(callid)
        if signature.Lwork in self.hideargs:
            ex.infer_lworks(callid)
        ex.update_data()

    # info string
    def sampler_about_str(self):
        """Generate an info string about the current sampler."""
        sampler = self.experiment.sampler
        info = "System:\t%s\n" % sampler["system_name"]
        info += "BLAS:\t%s\n" % sampler["blas_name"]
        if sampler["backend"] != "local":
            info += "  (via %s)\n" % sampler["backend"]
        info += "\n"
        info += "CPU:\t%s\n" % sampler["cpu_model"]
        info += "Mhz:\t%.2f\n" % (sampler["frequency"] / 1e6)
        info += "Cores:\t%d\n" % sampler["nt_max"]
        if "dflops/cycle" in sampler:
            info += "Gflops/s:\t%.2f (peak)" % (
                sampler["dflops/cycle"] * sampler["frequency"] *
                sampler["nt_max"] / 1e9
            )
        return info

    # loaders
    def sig_get(self, routine):
        """(Try to) get the Signature for a routine."""
        if routine not in self.sigs:
            try:
                self.sigs[routine] = elapsio.load_signature(routine)
                self.log("Loaded Signature for %r." % routine)
            except:
                self.sigs[routine] = None
                self.log("Can't load Signature for %r." % routine)
        return self.sigs[routine]

    def docs_get(self, routine):
        """(Try to) get the documentation for a routine."""
        if routine not in self.docs:
            try:
                self.docs[routine] = elapsio.load_docs(routine)
                self.log("Loaded documentation for %r." % routine)
            except:
                self.docs[routine] = None
                self.log("Can't load documentation for %r." % routine)
        return self.docs[routine]

    # UI utility

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

        ret = msgtypes[msgtype](self.UI_window, title, text, buttons)
        if callbackmap[ret] is not None:
            callbackmap[ret][0](*callbackmap[ret][1])

    def UI_alert(self, *args, **kwargs):
        """Alert a messagebox."""
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_varyM(self, name):
        """Generate vary menu for Operand."""
        ex = self.experiment
        data = ex.data[name]
        vary = data["vary"]

        if not vary["with"] and not ex.sumrange:
            action = QtGui.QAction(
                "Vary Operand", self.UI_window, checkable=True,
                toggled=self.on_vary_with_toggle
            )
            action.name = name
            action.with_ = "rep"
            return action

        menu = QtGui.QMenu("Vary Operand")

        withrep = QtGui.QAction(
            "With repetitions", menu,
            checkable=True, checked="rep" in vary["with"],
            toggled=self.on_vary_with_toggle
        )
        withrep.name = name
        withrep.with_ = "rep"
        menu.addAction(withrep)

        if ex.sumrange:
            withsumrange = QtGui.QAction(
                "With %s" % ex.sumrange[0], menu,
                checkable=True, checked=ex.sumrange[0] in vary["with"],
                toggled=self.on_vary_with_toggle
            )

            withsumrange.name = name
            withsumrange.with_ = ex.sumrange[0]
            menu.addAction(withsumrange)

        if not vary["with"]:
            return menu

        if len(data["dims"]) > 1:
            menu.addSeparator()
            alongG = QtGui.QActionGroup(menu, exclusive=True)
            for along in range(len(data["dims"])):
                text = "Along dimension %d" % (along + 1)
                if along < 3:
                    text += "\t" + u"\u2190\u2192\u2197"[along]

                alongA = QtGui.QAction(
                    text, menu,
                    checkable=True,
                    checked=vary["along"] == along,
                    toggled=self.on_vary_along_toggle,
                )
                alongA.name = name
                alongA.along = along
                alongG.addAction(alongA)
                menu.addAction(alongA)
            menu.addSeparator()

        text = "Set offset (%d)" % vary["offset"]
        offset = QtGui.QAction(text, menu,
                               triggered=self.on_vary_offset)
        offset.name = name
        menu.addAction(offset)

        return menu

    # UI setters
    def UI_setall(self):
        """Set all UI elements."""
        # sampler
        self.UI_hideargs_set()
        self.UI_sampler_set()
        self.UI_nthreads_set()
        self.UI_range_set()
        self.UI_nreps_set()
        self.UI_sumrange_set()
        self.UI_calls_parallel_set()
        self.UI_calls_set()

    def UI_hideargs_set(self):
        """Set UI element: hideargs options."""
        self.UI_setting += 1
        for UI_showarg, classes in self.UI_hideargs:
            UI_showarg.setChecked(self.hideargs >= classes)
        self.UI_setting -= 1

    def UI_sampler_set(self):
        """Set UI element: sampler."""
        self.UI_setting += 1
        self.UI_sampler.setCurrentIndex(
            self.UI_sampler.findText(self.experiment.sampler["name"])
        )
        self.UI_setting -= 1

    def UI_nthreads_set(self):
        """Set UI element: #threads."""
        self.UI_setting += 1
        self.UI_nthreads.clear()
        self.UI_nthreads.addItems(
            map(str, range(1, self.experiment.sampler["nt_max"] + 1))
        )
        if self.experiment.range:
            self.UI_nthreads.addItem(self.experiment.range[0])
        self.UI_nthreads.setCurrentIndex(
            self.UI_nthreads.findText(str(self.experiment.nthreads))
        )
        self.UI_setting -= 1

    def UI_range_set(self):
        """Set UI element: range."""
        self.UI_setting += 1
        userange = bool(self.experiment.range)
        self.UI_userange.setChecked(userange)
        self.UI_rangeW.setEnabled(userange)
        if self.experiment.range:
            range_ = self.experiment.range
        elif self.experiment_back.range:
            range_ = self.experiment_back.range
        else:
            range_ = (None, "")
        if range_[0] is None:
            range_[0] = ""
        self.UI_rangevar.setText(range_[0])
        self.UI_rangevals.setText(str(range_[1]))
        self.UI_setting -= 1

    def UI_nreps_set(self):
        """Set UI element: nreps."""
        self.UI_setting += 1
        self.UI_nreps.setText(str(self.experiment.nreps))
        self.UI_setting -= 1

    def UI_sumrange_set(self):
        """Set UI element: sumrange."""
        self.UI_setting += 1
        usesumrange = bool(self.experiment.sumrange)
        self.UI_usesumrange.setChecked(usesumrange)
        self.UI_sumrangeW.setEnabled(usesumrange)
        self.UI_sumrange_parallel.setCurrentIndex(
            1 if self.experiment.sumrange_parallel else 0
        )
        if usesumrange:
            sumrange = self.experiment.sumrange
        elif self.experiment_back.sumrange:
            sumrange = self.experiment_back.sumrange
        else:
            sumrange = ("", "")
        self.UI_sumrangevar.setText(sumrange[0])
        self.UI_sumrangevals.setText(str(sumrange[1]))
        self.UI_setting -= 1

    def UI_calls_parallel_set(self):
        """Set UI element: calls_parallel."""
        self.UI_setting += 1
        calls_parallel = self.experiment.calls_parallel
        self.UI_calls_parallel.setChecked(calls_parallel)
        self.UI_calls_parallelW.setEnabled(calls_parallel)
        self.UI_setting -= 1

    def UI_calls_set(self):
        """Set UI element: calls."""
        self.UI_setting += 1
        for callid, call in enumerate(self.experiment.calls):
            if callid >= self.UI_calls.count():
                UI_call = QCall(self, callid)
                self.UI_calls.addItem(UI_call)
                self.UI_calls.setItemWidget(UI_call, UI_call.widget)
            self.UI_calls.item(callid).setall()
        while self.UI_calls.count() > len(self.experiment.calls):
            self.UI_calls.takeItem(len(self.experiment.calls))
        self.UI_setting -= 1

    def UI_ranges_setvalid(self):
        """Set the "invlaid" property for the ranges."""
        ex = self.experiment
        if ex.range:
            self.UI_rangevar.setProperty("invalid", not ex.range[0])
            self.UI_rangevals.setProperty("invalid", not ex.range[1])
        if ex.sumrange:
            self.UI_sumrangevar.setProperty("invalid", not ex.sumrange[0])
            self.UI_sumrangevals.setProperty("invalid", not ex.sumrange[1])
        if ex.range and ex.sumrange:
            if ex.range[0] == ex.sumrange[0]:
                self.UI_rangevar.setProperty("invalid", True)
                self.UI_sumrangevar.setProperty("invalid", True)
        self.UI_nreps.setProperty("invalid", not ex.nreps)
        for UI_elem in (self.UI_rangevar, self.UI_sumrangevar,
                        self.UI_rangevals, self.UI_sumrangevals,
                        self.UI_nreps):
            UI_elem.style().unpolish(UI_elem)
            UI_elem.style().polish(UI_elem)
            UI_elem.update()

    # UI events
    @pyqtSlot()
    def on_jobprogress_timer(self):
        """Event: jobprogress timer interrupt."""
        # TODO

    def on_console_quit(self, *args):
        """Event: Ctrl-C from the console."""
        print("\r", end="")
        self.UI_window.close()
        if self.Qapp.viewer:
            self.Qapp.viewer.UI_window.close()
        self.Qapp.quit()

    @pyqtSlot()
    def on_window_close(self, event):
        """Event: close main window."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        settings.setValue("geometry", self.UI_window.saveGeometry())
        settings.setValue("windowState", self.UI_window.saveState())
        settings.setValue("Experiment", repr(self.experiment))
        settings.setValue("hideargs", repr(self.hideargs))
        self.log("Experiment saved.")

    @pyqtSlot()
    def on_submit(self):
        """Event: submit."""
        # TODO

    @pyqtSlot()
    def on_experiment_reset(self):
        """Event: reset experiment."""
        self.experiment_load(
            os.path.join(elapsio.setuppath, "default.ees")
        )
        self.UI_setall()

    @pyqtSlot()
    def on_experiment_load(self, report=False):
        """Event: load experiment."""
        filename = QtGui.QFileDialog.getOpenFileName(
            self.UI_window,
            "Load Experiment",
            elapsio.reportpath if report else elapsio.setuppath,
            "*.eer *.ees"
        )
        if filename:
            self.experiment_load(str(filename))
            self.UI_setall()

    @pyqtSlot()
    def on_experiment_load_report(self):
        """Event: load experiment from report."""
        self.on_experiment_load(True)

    @pyqtSlot()
    def on_experiment_save(self):
        """Event: save experiment."""
        filename = QtGui.QFileDialog.getSaveFileName(
            self.UI_window,
            "Save Setup",
            elapsio.setuppath,
            "*.ees"
        )
        if filename:
            elapsio.write_experiment(self.experiment, filename)

    @pyqtSlot()
    def on_viewer_start(self):
        """Event: start Viewer."""
        # TODO

    @pyqtSlot(bool)
    def on_hideargs_toggle(self, checked):
        """Event: toggle showarg."""
        if self.UI_setting:
            return
        classes = self.Qapp.sender().classes
        if checked:
            self.hideargs |= classes
        else:
            self.hideargs -= classes
        self.UI_hideargs_set()
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_sampler_change(self, value):
        """Event: change sampler."""
        if self.UI_setting:
            return
        value = str(value)
        self.experiment.sampler = self.samplers[value]
        # TODO: make experiment compliant

    @pyqtSlot(str)
    def on_nthreads_change(self, value):
        """Event: change #threads."""
        if self.UI_setting:
            return
        value = str(value)
        if not self.experiment.range or value != self.experiment.range[0]:
            value = int(value)
        self.experiment.nthreads = value

    @pyqtSlot(bool)
    def on_userange_toggle(self, checked):
        """Event: change if range is used."""
        if self.UI_setting:
            return
        ex = self.experiment
        if checked:
            if self.experiment_back.range:
                var, range_ = self.experiment_back.range
            else:
                var, range_ = "i", symbolic.Range((1, 1, 1,))
            if ex.sumrange and ex.sumrange[0] == var:
                var = "j" if ex.sumrange[0] == "i" else "i"
            ex.range = [var, range_]
        else:
            self.experiment_back.range = ex.range
            ex.substitute(**{ex.range[0]: max(ex.range[1])})
            ex.range = None
            ex.update_data()
            self.UI_nthreads_set()
            self.UI_calls_set()
        self.UI_range_set()

    @pyqtSlot(str)
    def on_rangevar_change(self, value):
        """Event: change range variable."""
        if self.UI_setting:
            return
        value = str(value)
        ex = self.experiment
        ex.substitute(**{ex.range[0]: symbolic.Symbol(value)})
        ex.range[0] = value
        ex.update_data()
        self.UI_ranges_setvalid()
        self.UI_nthreads_set()
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_rangevals_change(self, value):
        """Event: change range."""
        if self.UI_setting:
            return
        try:
            self.experiment.range[1] = symbolic.Range(str(value))
        except:
            self.experiment.range[1] = symbolic.Range()
        self.experiment.update_data()
        self.UI_ranges_setvalid()
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_nreps_change(self, value):
        """Event: change #repetitions."""
        if self.UI_setting:
            return
        value = str(value)
        if value:
            self.experiment.nreps = int(value)
        else:
            self.experiment.nreps = 0
        self.UI_ranges_setvalid()

    @pyqtSlot(bool)
    def on_usesumrange_toggle(self, checked):
        """Event: change if sumrange is used."""
        if self.UI_setting:
            return
        ex = self.experiment
        if value:
            if self.experiment_back.sumrange:
                var, range_ = self.experiment_back.sumrange
            else:
                var, range_ = "j", symbolic.Range((1, 1, 1))
            if ex.range and ex.range[0] == var:
                var = "j" if ex.range[0] == "i" else "i"
            ex.sumrange = [var, range_]
        else:
            self.experiment_back.sumrange = ex.sumrange
            sumrange_vals = self.sumrange[1]
            if ex.range:
                sumrange_vals = symbolic.simplify(
                    sumrange_vals, **{ex.range[0]: max(ex.range[1])}
                )
            ex.substitute(**{ex.sumrange[0]: sumrange_vals})
            ex.sumrange = None
        self.UI_sumrange_set()

    @pyqtSlot(int)
    def on_sumrange_parallel_change(self, value):
        """Event: change if sumrange is in parallel."""
        if self.UI_setting:
            return
        value = bool(value)
        self.experiment.sumrange_parallel = value

    @pyqtSlot(str)
    def on_sumrangevar_change(self, value):
        """Event: change sumrange variable."""
        if self.UI_setting:
            return
        value = str(value)
        ex = self.experiment
        ex.substitute(**{ex.sumrange[0]: symbolic.Symbol(value)})
        ex.sumrange[0] = value
        ex.update_data()
        self.UI_ranges_setvalid()
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_sumrangevals_change(self, value):
        """Event: change sumrange."""
        if self.UI_setting:
            return
        ex = self.experiment
        symdict = {}
        range_ = ex.range
        if range_:
            symdict[range_[0]] = symbolic.Symbol(range_[0])
        try:
            ex.sumrange[1] = symbolic.Range(str(value), **symdict)
        except:
            ex.sumrange[1] = symbolic.Range()
        ex.update_data()
        self.UI_ranges_setvalid()
        self.UI_calls_set()

    @pyqtSlot(bool)
    def on_calls_parallel_toggle(self, value):
        """Event: change if calls are in parallel."""
        if self.UI_setting:
            return
        self.experiment.calls_parallel = bool(value)
        self.UI_calls_parallel_set()

    @pyqtSlot()
    def on_calls_reorder(self):
        """Event: change call order."""
        if self.UI_setting:
            return
        calls = self.experiment.calls
        self.experiment.calls = []
        for idx in range(self.UI_calls.count()):
            self.experiment.calls.append(
                calls[self.UI_calls.item(idx).fixcallid]
            )
        self.UI_calls_set()

    def on_calls_focusout(self, event):
        """Event: unfocus calls."""
        for callid in range(self.UI_calls.count()):
            self.UI_calls.setItemSelected(self.UI_calls.item(callid), False)

    def on_routine_set(self, callid, value):
        """Event: Set routine value."""
        ex = self.experiment
        try:
            if value not in ex.sampler["kernels"]:
                # not a kernel
                ex.calls[callid] = [value]
                raise Exception

            minsig = ex.sampler["kernels"][value]
            ex.calls[callid] = signature.BasicCall(
                minsig, *((len(minsig) - 1) * [None])
            )
            sig = self.sig_get(value)
            if not sig:
                # no Signature
                raise Exception

            if len(sig) != len(minsig):
                # wrong Signature
                self.UI_alert(
                    ("Kernel %r of Sampler %r has %d arguments,\n"
                        "but Signature '%s' requires %d.\n"
                        "Signature ignored.")
                    % (value, ex.sampler["name"], len(minsig) - 1, sig,
                       len(sig) - 1)
                )
                raise Exception

            try:
                call = sig()
            except:
                # Signature not working
                self.UI_alert(
                    "Can't use Signature %r\nSignature Ignored" % sig
                )
                raise Exception

            names = list(ex.data)
            for argid, arg in enumerate(sig):
                if isinstance(arg, signature.Dim):
                    call[argid] = self.defaultdim
                    continue
                if not isinstance(arg, signature.Data):
                    continue
                try:
                    name = next(n for n in string.ascii_uppercase
                                if n not in names)
                except:
                    name = next(
                        n for n in (
                            "%s%s" % (l, d) for d in itertools.count(1)
                            for l in string.ascii_uppercasei
                        ) if n not in names
                    )
                call[argid] = name
                names.append(name)

            ex.calls[callid] = call
            ex.infer_lds(callid)
            ex.infer_lworks(callid)
        except:
            pass
        ex.update_data()
        self.UI_calls_set()

    def on_arg_set(self, callid, argid, value):
        """Event: Set argument value."""
        if self.UI_setting:
            return
        if argid == 0:
            self.on_routine_set(callid, value)
            return
        ex = self.experiment
        call = ex.calls[callid]
        arg = call.sig[argid]
        parsed = None
        try:
            parsed = ex.ranges_parse(value)
        except:
            pass
        if isinstance(arg, signature.Flag):
            call[argid] = value
        elif isinstance(arg, signature.Dim):
            call[argid] = parsed
            ex.apply_connections(callid, argid)
            if signature.Ld in self.hideargs:
                ex.infer_lds(callid)
            if signature.Lwork in self.hideargs:
                ex.infer_lworks(callid)
        elif isinstance(arg, signature.Data):
            if value in self.data:
                self.data_override(callid, argid, value)
                return
            call[argid] = value
        elif isinstance(arg, signature.Arg):
            call[argid] = parsed
        else:
            if arg != "char*":
                try:
                    call[argid] = ex.ranges_parse(value)
                except:
                    pass
        ex.update_data()
        self.UI_calls_set()

    @pyqtSlot(QtCore.QPoint)
    def on_calls_rightclick(self, pos):
        """Event: right click in calls."""
        if self.UI_setting:
            return
        globalpos = self.UI_calls.viewport().mapToGlobal(pos)
        item = self.UI_calls.itemAt(pos)
        if item:
            self.UI_call_contextmenu.item = item
            self.UI_call_contextmenu.exec_(globalpos)
        else:
            self.UI_calls_contextmenu.exec_(globalpos)

    @pyqtSlot()
    def on_call_add(self):
        """Event: add call."""
        if self.UI_setting:
            return
        self.experiment.calls.append([""])
        self.UI_calls_set()
        self.UI_calls.item(
            len(self.experiment.calls) - 1
        ).UI_args[0].setFocus()

    @pyqtSlot()
    def on_call_remove(self):
        """Event: remove call."""
        if self.UI_setting:
            return
        self.experiment.calls.pop(self.UI_call_contextmenu.item.callid)
        self.UI_calls_set()

    @pyqtSlot()
    def on_call_clone(self):
        """Event: clone call."""
        if self.UI_setting:
            return
        self.experiment.calls.append(
            self.experiment.calls[self.UI_call_contextmenu.item.callid].copy()
        )
        self.UI_calls_set()

    def on_infer_ld(self, callid, argid):
        """Event: infer ld."""
        if self.UI_setting:
            return
        self.experiment.infer_ld(callid, argid)
        self.UI_calls_set()

    @pyqtSlot()
    def on_infer_lwork(self, callid, argid):
        """Event: infer lwork."""
        if self.UI_setting:
            return
        self.experiment.infer_lwork(callid, argid)
        self.UI_calls_set()

    @pyqtSlot(bool)
    def on_vary_with_toggle(self, checked):
        """Event: changed vary with."""
        sender = self.Qapp.sender()
        ex = self.experiment
        vary = ex.data[sender.name]["vary"]
        if checked:
            vary["with"].add(sender.with_)
        else:
            vary["with"].discard(sender.with_)
        self.experiment_infer_update()
        self.UI_calls_set()

    @pyqtSlot(bool)
    def on_vary_along_toggle(self, checked):
        """Event: changed vary along."""
        sender = self.Qapp.sender()
        ex = self.experiment
        vary = ex.data[sender.name]["vary"]
        vary["along"] = sender.along
        self.experiment_infer_update()
        self.UI_calls_set()

    @pyqtSlot()
    def on_vary_offset(self):
        """Event: set vary offset."""
        sender = self.Qapp.sender()
        name = sender.name
        value, ok = QtGui.QInputDialog.getText(
            self.UI_window, "Vary offset for %s" % name,
            "Vary offset for %s:" % name,
        )
        if not ok:
            return
        try:
            value = self.experiment.ranges_parse(str(value))
        except:
            self.UI_alert("Invalid offset:\n%s" % value)
        self.experiment.data[name]["vary"]["offset"] = value
        self.experiment_infer_update()
        self.UI_calls_set()


def main():
    """Main entry point."""
    if "--reset" in sys.argv:
        PlayMat(reset=True).start()
        return
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename[-4:] in (".ees", ".eer"):
            PlayMat(load=filename).start()
            return
    PlayMat().start()


if __name__ == "__main__":
    main()
