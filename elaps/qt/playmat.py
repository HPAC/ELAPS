#!/usr/bin/env python
"""GUI for Experiments."""
from __future__ import division, print_function

import elaps.defines as defines
import elaps.io
import elaps.symbolic as symbolic
import elaps.signature as signature

from elaps.qt import QCall, QJobProgress

import sys
import os
import string
import itertools
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot


class PlayMat(QtGui.QMainWindow):

    """GUI for Experiment."""

    def __init__(self, app=None, load=None, reset=False):
        """Initilialize the PlayMat."""
        if app:
            self.Qapp = app
        else:
            self.Qapp = QtGui.QApplication(sys.argv)
            self.Qapp.viewer = None
        self.Qapp.playmat = self
        QtGui.QMainWindow.__init__(self)
        self.samplers = elaps.io.load_all_samplers()
        if not self.samplers:
            self.alert("ERROR: No Samplers found!")
            sys.exit()
        self.docs = {}
        self.sigs = {}
        self.papi_names = elaps.io.load_papinames()
        self.last_filebase = None

        # set up UI
        self.UI_init()
        self.hideargs = set([signature.Ld, signature.Inc, signature.Work,
                             signature.Lwork, signature.Info])
        if not reset:
            try:
                self.UI_settings_load()
                self.UI_jobprogress.hide()
            except:
                pass

        # set experiment
        self.experiment = None
        if load:
            try:
                self.experiment_load(load)
            except:
                self.alert("ERROR: Can't load %r" % load)
        if not self.experiment and not reset:
            try:
                self.experiment_qt_load()
            except:
                pass
        if not self.experiment:
            self.experiment_reset()
        self.experiment_back = self.experiment.copy()
        self.experiment.update_data()

        self.UI_setall()

    def UI_init(self):
        """Initialize all GUI elements."""
        self.UI_setting = 1

        # window
        self.pyqtConfigure(
            windowTitle="ELAPS:PlayMat", unifiedTitleAndToolBarOnMac=True
        )
        self.setCorner(QtCore.Qt.TopRightCorner, QtCore.Qt.TopDockWidgetArea)
        self.statusBar()

        # DEBUG: print experiment
        QtGui.QShortcut(
            QtGui.QKeySequence.Print, self, lambda: print(self.experiment)
        )

        def create_menus():
            """Create all menus."""
            menu = self.menuBar()

            # file
            fileM = menu.addMenu("File")

            # file > submit
            self.UI_submitA = QtGui.QAction(
                "Run", self, shortcut=QtGui.QKeySequence("Ctrl+R"),
                triggered=self.on_submit
            )
            fileM.addAction(self.UI_submitA)

            # submit last shortcut
            QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+R"), self, self.on_submit_last
            )

            # file
            fileM.addSeparator()

            # file > reset
            fileM.addAction(QtGui.QAction(
                "Reset Experiment", self, triggered=self.on_experiment_reset
            ))

            # file > load
            fileM.addAction(QtGui.QAction(
                "Load Experiment ...", self,
                shortcut=QtGui.QKeySequence.Open,
                triggered=self.on_experiment_load
            ))

            # load report shortcut
            QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+O"), self,
                self.on_experiment_load_report
            )

            # fie > save
            fileM.addAction(QtGui.QAction(
                "Save Experiment ...", self,
                shortcut=QtGui.QKeySequence.Save,
                triggered=self.on_experiment_save
            ))

            # file
            fileM.addSeparator()

            fileM.addAction(QtGui.QAction(
                "Start Viewer", self, triggered=self.on_viewer_start
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
                    desc, self, checkable=True, toggled=self.on_hideargs_toggle
                )
                action.classes = set(classes)
                self.UI_viewM.addAction(action)
                self.UI_hideargs.append((action, set(classes)))

        def create_toolbar():
            """Create all toolbars."""
            # sampler
            self.UI_sampler = QtGui.QComboBox()
            self.UI_sampler.addItems(sorted(self.samplers.keys()))
            self.UI_sampler.currentIndexChanged[str].connect(
                self.on_sampler_change
            )

            samplerT = self.addToolBar("Sampler")
            samplerT.pyqtConfigure(movable=False, objectName="Sampler")
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            samplerT.addWidget(self.UI_sampler)

            # #threads
            self.UI_nthreads = QtGui.QComboBox()
            self.UI_nthreads.currentIndexChanged[str].connect(
                self.on_nthreads_change
            )

            nthreadsT = self.addToolBar("#threads")
            nthreadsT.pyqtConfigure(movable=False, objectName="#threads")
            nthreadsT.addWidget(QtGui.QLabel("#threads:"))
            nthreadsT.addWidget(self.UI_nthreads)

            # submit
            samplerT = self.addToolBar("Submit")
            samplerT.pyqtConfigure(movable=False, objectName="Submit")

            # spacer
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
            samplerT.addWidget(spacer)

            # submit
            self.UI_submit = QtGui.QAction(self.style().standardIcon(
                QtGui.QStyle.SP_DialogOkButton
            ), "Run", self, triggered=self.on_submit)
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
                minimumWidth=32, textChanged=self.on_rangevals_change
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
            # self.UI_nreps.setValidator(QtGui.QIntValidator(bottom=1))
            self.UI_nreps.setValidator(QtGui.QIntValidator(1, 1000000, self))
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
                minimumWidth=32, textChanged=self.on_sumrangevals_change
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
            rangesL.setRowStretch(4, 1)

            rangesW = QtGui.QWidget()
            rangesW.setLayout(rangesL)

            rangesD = QtGui.QDockWidget(
                "Ranges", objectName="Ranges",
                features=QtGui.QDockWidget.DockWidgetVerticalTitleBar,
            )
            rangesD.setWidget(rangesW)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, rangesD)

        def create_note():
            """Create the note input."""
            self.UI_note = QtGui.QTextEdit(
                textChanged=self.on_note_change
            )

            noteD = QtGui.QDockWidget(
                "Note", objectName="Note",
                features=(QtGui.QDockWidget.DockWidgetVerticalTitleBar |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            noteD.setWidget(self.UI_note)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, noteD)

        def create_calls():
            """Create the calls list and add button (central widget)."""
            self.UI_calls = QtGui.QListWidget(
                verticalScrollMode=QtGui.QListWidget.ScrollPerPixel,
                selectionMode=QtGui.QListWidget.ExtendedSelection,
                dragDropMode=QtGui.QListWidget.InternalMove,
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                customContextMenuRequested=self.on_calls_rightclick
            )
            self.UI_calls.model().layoutChanged.connect(self.on_calls_reorder)

            self.setCentralWidget(self.UI_calls)

            # shortcuts
            QtGui.QShortcut(
                QtGui.QKeySequence.New, self.UI_calls,
                activated=self.on_call_add
            )
            QtGui.QShortcut(
                QtGui.QKeySequence.Close, self.UI_calls,
                activated=self.on_call_remove
            )

            # context menus
            self.UI_call_contextmenu = QtGui.QMenu()
            self.UI_calls_contextmenu = QtGui.QMenu()

            # add
            add = QtGui.QAction(
                "Add call", self, shortcut=QtGui.QKeySequence.New,
                triggered=self.on_call_add

            )
            self.UI_call_contextmenu.addAction(add)
            self.UI_calls_contextmenu.addAction(add)

            # remove
            self.UI_call_contextmenu.addAction(QtGui.QAction(
                "Remove call", self,
                shortcut=QtGui.QKeySequence.Close,
                triggered=self.on_call_remove
            ))

            # clone
            self.UI_call_contextmenu.addAction(QtGui.QAction(
                "Clone call", self, triggered=self.on_call_clone
            ))

            self.UI_call_contextmenu.addSeparator()
            self.UI_calls_contextmenu.addSeparator()

            self.UI_call_contextmenu.addMenu(self.UI_viewM)
            self.UI_calls_contextmenu.addMenu(self.UI_viewM)

        def create_counters():
            """Create the counters widget."""
            countersW = QtGui.QWidget()
            countersW.setLayout(QtGui.QVBoxLayout())
            countersW.layout().insertStretch(100, 1)

            self.UI_countersD = QtGui.QDockWidget(
                "PAPI counters", objectName="PAPI counters",
                features=(QtGui.QDockWidget.DockWidgetVerticalTitleBar |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            self.UI_countersD.setWidget(countersW)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.UI_countersD)
            self.UI_countersD.hide()

            self.UI_countersD.widgets = []

        def create_style():
            """Set style options."""
            # stylesheet
            self.setStyleSheet("""
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
        create_toolbar()
        create_ranges()
        create_note()
        create_calls()
        create_counters()
        create_style()

        self.UI_jobprogress = QJobProgress(self)

        self.show()

        self.UI_setting -= 1

    def UI_settings_load(self):
        """Load Qt settings."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        self.hideargs = eval(str(settings.value("hideargs", type=str)),
                             signature.__dict__)
        self.UI_setting += 1
        self.restoreGeometry(settings.value("geometry",
                                            type=QtCore.QByteArray))
        self.restoreState(settings.value("windowState",
                                         type=QtCore.QByteArray))
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

    # experiment routines
    def experiment_set(self, ex):
        """Insert own/new objects into loaded experiment."""
        # own Sampler
        if ex.sampler is None or ex.sampler["name"] not in self.samplers:
            ex.sampler = self.samplers[min(self.samplers)]
        else:
            ex.sampler = self.samplers[ex.sampler["name"]]
        ex.apply_sampler_restrictions()

        # own Signatures
        newcalls = []
        for call in ex.calls:
            sig = self.sig_get(call[0])
            if sig:
                newcalls.append(sig(*call[1:]))
            else:
                newcalls.append(call)
        ex.calls = newcalls

        # update
        ex.update_data()

        self.experiment = ex

    def experiment_reset(self):
        """Reset experiment to default."""
        self.experiment_load(
            os.path.join(elaps.io.experimentpath,
                         "default." + defines.experiment_extension)
        )

    def experiment_qt_load(self):
        """Load Experiment from Qt setting."""
        ex = elaps.io.load_experiment_string(str(
            QtCore.QSettings("HPAC", "ELAPS:PlayMat").value("Experiment",
                                                            type=str)
        ))
        self.experiment_set(ex)
        self.log("Loaded last Experiment")

    def experiment_load(self, filename):
        """Load Experiment from a file."""
        ex = elaps.io.load_experiment(filename)
        self.experiment_set(ex)
        self.log("Loaded Experiment from %r." % os.path.relpath(filename))

    def experiment_write(self, filename):
        """Write Experiment to a file."""
        elaps.io.wrte_experiment(self.experiment, filename)
        self.log("Written Experiment to %r." % os.path.relpath(filename))

    def experiment_infer_update_set(self, callid=None):
        """Infer Ld and Lwork (if not showing) and update_data()."""
        ex = self.experiment
        if signature.Ld in self.hideargs:
            ex.infer_lds(callid)
        if signature.Lwork in self.hideargs:
            ex.infer_lworks(callid)
        ex.update_data()
        self.UI_submit_setenabled()
        self.UI_calls_set()

    def experiment_submit(self, filebase):
        """Submit a job."""
        ex = self.experiment
        backend = ex.sampler["backend"]
        jobid = ex.submit(filebase)
        self.last_filebase = filebase
        self.UI_jobprogress.add_job(filebase, jobid, ex)
        self.log("Submitted job for %r to %r." % (filebase, backend.name))

    # loaders
    def sig_get(self, routine):
        """(Try to) get the Signature for a routine."""
        if routine not in self.sigs:
            try:
                self.sigs[routine] = elaps.io.load_signature(routine)
                self.log("Loaded Signature for %r." % routine)
            except:
                self.sigs[routine] = None
                self.log("Can't load Signature for %r." % routine)
        return self.sigs[routine]

    def docs_get(self, routine):
        """(Try to) get the documentation for a routine."""
        if routine not in self.docs:
            try:
                self.docs[routine] = elaps.io.load_doc(routine)
                self.log("Loaded documentation for %r." % routine)
            except:
                self.docs[routine] = None
                self.log("Can't load documentation for %r." % routine)
        return self.docs[routine]

    # viewer
    def viewer_start(self, *args):
        """Start the Viewer."""
        from viewer import Viewer
        Viewer(*args, app=self.Qapp)

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

        ret = msgtypes[msgtype](self, title, text, buttons)
        if callbackmap[ret] is not None:
            callbackmap[ret][0](*callbackmap[ret][1])

    def UI_alert(self, *args, **kwargs):
        """Alert a messagebox."""
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

    def UI_varyactions(self, name):
        """Generate vary menu for Operand."""
        ex = self.experiment
        data = ex.data[name]
        vary = data["vary"]

        actions = []

        withrep = QtGui.QAction(
            "Vary with repetitions", self,
            checkable=True, checked="rep" in vary["with"],
            toggled=self.on_vary_with_toggle
        )
        withrep.name = name
        withrep.with_ = "rep"
        actions.append(withrep)

        if ex.sumrange:
            withsumrange = QtGui.QAction(
                "Vary with %s" % ex.sumrange[0], self,
                checkable=True, checked=ex.sumrange[0] in vary["with"],
                toggled=self.on_vary_with_toggle
            )

            withsumrange.name = name
            withsumrange.with_ = ex.sumrange[0]
            actions.append(withsumrange)

        if not vary["with"]:
            return actions

        if len(data["dims"]) > 1:
            actions.append(None)
            alongG = QtGui.QActionGroup(self, exclusive=True)
            for along in range(len(data["dims"])):
                if along < 3:
                    text = "Vary along %s (dim %d)" % (
                        u"\u2193\u2192\u2197"[along],
                        along + 1
                    )
                else:
                    text = "Vary along dim %d" % (along + 1)

                alongA = QtGui.QAction(
                    text, self,
                    checkable=True,
                    checked=vary["along"] == along,
                    toggled=self.on_vary_along_toggle,
                )
                alongA.name = name
                alongA.along = along
                alongG.addAction(alongA)
                actions.append(alongA)

        actions.append(None)
        text = "Change vary offset (%s)" % vary["offset"]
        offset = QtGui.QAction(
            text, self, triggered=self.on_vary_offset
        )
        offset.name = name
        actions.append(offset)

        actions.append(None)

        return actions

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
        self.UI_submit_setenabled()
        self.UI_note_set()
        self.UI_counters_set()
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
            range_ = ["", ""]
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
            sumrange = ["", ""]
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

    def UI_note_set(self):
        """Set UI element: note."""
        self.UI_setting += 1
        self.UI_note.setPlainText(self.experiment.note or "")
        self.UI_setting -= 1

    def UI_counters_set(self):
        """Set UI elemnt: counters."""
        self.UI_setting += 1
        ex = self.experiment
        if not ex.sampler["papi_enabled"]:
            self.UI_countersD.hide()
            self.UI_setting -= 1
            return

        # PAPI is available
        counterWs = self.UI_countersD.widgets
        for counterid in range(ex.sampler["papi_counters_max"]):
            if counterid >= len(counterWs):
                # create widgets as needed
                counterW = QtGui.QComboBox(
                    currentIndexChanged=self.on_counter_change
                )
                counterW.addItem("", QtCore.QVariant(""))
                for i, name in enumerate(ex.sampler["papi_counters_avail"]):
                    event = self.papi_names[name]
                    counterW.addItem(event["short"], QtCore.QVariant(name))
                    counterW.setItemData(i + 1, name + "\n" + event["long"],
                                         QtCore.Qt.ToolTipRole)
                self.UI_countersD.widget().layout().insertWidget(counterid,
                                                                 counterW)
                counterWs.append(counterW)
            else:
                counterW = counterWs[counterid]
            # set values
            if counterid < len(ex.papi_counters):
                counterW.setCurrentIndex(counterW.findData(
                    QtCore.QVariant(ex.papi_counters[counterid])
                ))
            else:
                counterW.setCurrentIndex(0)
            counterW.setVisible(counterid <= len(ex.papi_counters))
        # remove additional widgets
        while len(counterWs) > ex.sampler["papi_counters_max"]:
            counterWs[-1].deleteLater()
            del counterWs[-1]
        self.UI_countersD.show()
        self.UI_setting -= 1

    def UI_submit_setenabled(self):
        """En/Disable the submit Action."""
        try:
            self.experiment.check_sanity(True)
            enabled = True
            tooltip = "Run"
        except Exception as e:
            enabled = False
            tooltip = str(e)
        self.UI_submitA.setEnabled(enabled)
        self.UI_submit.setEnabled(enabled)
        self.UI_submit.setToolTip(tooltip)

    def UI_ranges_setvalid(self):
        """Set the "invlaid" property for the ranges."""
        ex = self.experiment
        if ex.range:
            self.UI_rangevar.setProperty("invalid", not ex.range[0])
            self.UI_rangevals.setProperty("invalid", not ex.range[1])
        if ex.sumrange:
            self.UI_sumrangevar.setProperty("invalid", ex.sumrange[0] is None)
            self.UI_sumrangevals.setProperty("invalid", ex.sumrange[1] is None)
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
    def on_console_quit(self, *args):
        """Event: Ctrl-C from the console."""
        print("\r", end="")
        self.close()
        if self.Qapp.viewer:
            self.Qapp.viewer.close()
        self.Qapp.quit()

    def closeEvent(self, event):
        """Event: close main window."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("Experiment", repr(self.experiment))
        settings.setValue("hideargs", repr(self.hideargs))
        self.log("Experiment saved.")

    @pyqtSlot()
    def on_submit(self):
        """Event: submit."""
        if self.Qapp.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            if self.last_filebase:
                self.on_submit_last()
                return

        reportpath = elaps.io.reportpath
        if self.last_filebase:
            reportpath = "%s.%s" % (self.last_filebase,
                                    defines.report_extension)
        filename = QtGui.QFileDialog.getSaveFileName(
            self, "Generate Report", reportpath,
            "*." + defines.report_extension
        )
        if not filename:
            return
        filebase = str(filename)
        if filebase[-4:] == "." + defines.report_extension:
            filebase = filebase[:-4]
        self.experiment_submit(filebase)

    @pyqtSlot()
    def on_submit_last(self):
        """Event: resubmit last job."""
        if not self.last_filebase:
            self.on_submit()
            return
        self.experiment_submit(self.last_filebase)

    @pyqtSlot()
    def on_experiment_reset(self):
        """Event: reset experiment."""
        self.experiment_reset()
        self.UI_setall()

    @pyqtSlot()
    def on_experiment_load(self, report=False):
        """Event: load experiment."""
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Load Experiment",
            elaps.io.reportpath if report else elaps.io.experimentpath,
            " ".join("*." + ext for ext in defines.experiment_extensions)
        )
        if not filename:
            return
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
            self,
            "Save Setup",
            elaps.io.experimentpath,
            "*." + defines.experiment_extension
        )
        if not filename:
            return
        filebase = str(filename)
        if filebase[-4:] == "." + defines.experiment_extension:
            filebase = filebase[:-4]
        filename = "%s.%s" % (filebase, defines.experiment_extension)
        elaps.io.write_experiment(self.experiment, filename)

    @pyqtSlot()
    def on_viewer_start(self):
        """Event: start Viewer."""
        if not self.Qapp.viewer:
            self.viewer_start()
        self.Qapp.viewer.show()

    # @pyqtSlot(bool)  # sender() pyqt bug
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
    def on_note_change(self):
        """Event: changed note."""
        if self.UI_setting:
            return
        self.experiment.note = self.UI_note.toPlainText()

    @pyqtSlot(str)
    def on_sampler_change(self, value):
        """Event: change sampler."""
        if self.UI_setting:
            return
        value = str(value)
        self.experiment.sampler = self.samplers[value]
        # TODO: warn
        self.experiment.apply_sampler_restrictions()
        self.UI_setall()

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
            self.UI_submit_setenabled()
            self.UI_calls_set()
        self.UI_nthreads_set()
        self.UI_range_set()
        self.UI_calls_set()

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
        self.UI_submit_setenabled()
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_rangevals_change(self, value):
        """Event: change range."""
        if self.UI_setting:
            return
        try:
            self.experiment.range[1] = symbolic.Range(str(value))
        except:
            self.experiment.range[1] = None
        self.UI_ranges_setvalid()
        self.experiment_infer_update_set()

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
        self.experiment_infer_update_set()

    @pyqtSlot(bool)
    def on_usesumrange_toggle(self, checked):
        """Event: change if sumrange is used."""
        if self.UI_setting:
            return
        ex = self.experiment
        if checked:
            if self.experiment_back.sumrange:
                var, range_ = self.experiment_back.sumrange
            else:
                var, range_ = "j", symbolic.Range((1, 1, 1))
            if ex.range and ex.range[0] == var:
                var = "j" if ex.range[0] == "i" else "i"
            ex.sumrange = [var, range_]
        else:
            for data in ex.data.values():
                data["vary"]["with"].discard(ex.sumrange[0])
            self.experiment_back.sumrange = ex.sumrange
            sumrange_vals = ex.sumrange[1]
            if ex.range:
                sumrange_vals = symbolic.simplify(
                    sumrange_vals, **{ex.range[0]: max(ex.range[1])}
                )
            ex.substitute(**{ex.sumrange[0]: sumrange_vals})
            ex.sumrange = None
        self.UI_sumrange_set()
        self.UI_calls_set()

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
        self.UI_submit_setenabled()
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
            ex.sumrange[1] = None
        self.UI_ranges_setvalid()
        self.experiment_infer_update_set()

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
        calls = self.experiment.calls
        self.experiment.calls = []
        for idx in range(self.UI_calls.count()):
            self.experiment.calls.append(
                calls[self.UI_calls.item(idx).fixcallid]
            )
        self.UI_calls_set()

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
                    call[argid] = defines.default_dim
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
        self.experiment_infer_update_set()

    def on_dataarg_set(self, callid, argid, value):
        """Event Set data argument value."""
        ex = self.experiment
        call = ex.calls[callid]
        if value not in ex.data:
            call[argid] = value
            self.experiment_infer_update_set()
            return
        # data already existst
        data = ex.data[value]
        arg = call.sig[argid]
        sender = self.Qapp.sender()
        if data["type"] != type(arg):
            self.UI_alert("Incompatible data types for %r: %r and %r." %
                          (value, data["type"].typename, type(arg).typename))
            sender.clearFocus()
            self.experiment_infer_update_set()
            sender.setFocus()
        # try and check if data changes:
        oldvalue = call[argid]
        call[argid] = value
        connections = ex.get_connections()
        call[argid] = oldvalue
        if any(
            ex.calls[callid][argid] != ex.calls[callid2][argid2]
            for (callid, argid), connections2 in connections.items()
            for callid2, argid2 in connections2
        ):
            ret = QtGui.QMessageBox.warning(
                self, "Incompatible sizes for %s" % value,
                "Dimensions will be adjusted automatically.",
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
            )
            if ret == QtGui.QMessageBox.Ok:
                call[argid] = value
                for argid in range(len(call)):
                    ex.apply_connections(callid, argid)
                self.experiment_infer_update_set()
            else:
                sender.clearFocus()
                self.experiment_infer_update_set()
                sender.setFocus()
        else:
            call[argid] = value
            self.experiment_infer_update_set()

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
        elif isinstance(arg, signature.Data):
            self.on_dataarg_set(callid, argid, value)
            return
        elif isinstance(arg, signature.Arg):
            call[argid] = parsed
        else:
            if arg != "char*":
                try:
                    call[argid] = ex.ranges_parse(value)
                except:
                    pass
        self.experiment_infer_update_set()

    @pyqtSlot(QtCore.QPoint)
    def on_calls_rightclick(self, pos):
        """Event: right click in calls."""
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
        self.experiment.calls.append([""])
        self.UI_submit_setenabled()
        self.UI_calls_set()
        callid = len(self.experiment.calls) - 1
        self.UI_calls.item(callid).UI_args[0].setFocus()
        selected_callid = self.UI_calls.currentRow()
        if selected_callid != -1:
            self.UI_calls.setItemSelected(self.UI_calls.item(selected_callid),
                                          False)
            self.UI_calls.setCurrentRow(callid)

    @pyqtSlot()
    def on_call_remove(self):
        """Event: remove call."""
        callid = self.UI_calls.currentRow()
        if callid == -1:
            return
        self.experiment.calls.pop(callid)
        self.UI_submit_setenabled()
        self.UI_calls_set()
        if callid:
            self.UI_calls.setCurrentRow(callid - 1)

    @pyqtSlot()
    def on_call_clone(self):
        """Event: clone call."""
        self.experiment.calls.append(
            self.experiment.calls[self.UI_call_contextmenu.item.callid].copy()
        )
        self.UI_submit_setenabled()
        self.UI_calls_set()

    def on_infer_ld(self, callid, argid):
        """Event: infer ld."""
        self.experiment.infer_ld(callid, argid)
        self.UI_submit_setenabled()
        self.UI_calls_set()

    @pyqtSlot()
    def on_infer_lwork(self, callid, argid):
        """Event: infer lwork."""
        self.experiment.infer_lwork(callid, argid)
        self.UI_submit_setenabled()
        self.UI_calls_set()

    # @pyqtSlot(bool)  # sender() pyqt bug
    def on_vary_with_toggle(self, checked):
        """Event: changed vary with."""
        sender = self.Qapp.sender()
        data = self.experiment.data[sender.name]
        vary = data["vary"]
        if checked:
            if not vary["with"]:
                vary["offset"] = 0
                vary["along"] = len(data["dims"]) - 1
            vary["with"].add(sender.with_)
        else:
            vary["with"].discard(sender.with_)
        self.experiment_infer_update_set()

    # @pyqtSlot(bool)  # sender() pyqt bug
    def on_vary_along_toggle(self, checked):
        """Event: changed vary along."""
        sender = self.Qapp.sender()
        ex = self.experiment
        vary = ex.data[sender.name]["vary"]
        vary["along"] = sender.along
        self.experiment_infer_update_set()

    # @pyqtSlot()  # sender() pyqt bug
    def on_vary_offset(self):
        """Event: set vary offset."""
        sender = self.Qapp.sender()
        name = sender.name
        vary = self.experiment.data[name]["vary"]
        value, ok = QtGui.QInputDialog.getText(
            self, "Vary offset for %s" % name,
            "Vary offset for %s:" % name, text=str(vary["offset"])
        )
        if not ok:
            return
        value = value or "0"
        try:
            value = self.experiment.ranges_parse(str(value))
        except:
            self.UI_alert("Invalid offset:\n%s" % value)
        vary["offset"] = value
        self.experiment_infer_update_set()

    @pyqtSlot()
    def on_counter_change(self):
        """Event: changed PAPI counter."""
        if self.UI_setting:
            return
        counternames = [
            str(widget.itemData(widget.currentIndex()).toString())
            for widget in self.UI_countersD.widgets
        ]
        self.experiment.papi_counters = [name for name in counternames if name]
        self.UI_counters_set()

    def on_open_viewer(self, filename):
        """Event: open report in Viewer."""
        if not self.Qapp.viewer:
            self.viewer_start(filename)
            return
        self.Qapp.viewer.report_load(filename, True)
        self.Qapp.viewer.UI_setall()
        self.Qapp.viewer.show()
        self.Qapp.viewer.raise_()
