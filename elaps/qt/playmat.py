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
        self.reportname = defines.default_reportname
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

        # DEBUG: print Experiment
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

            # load Report shortcut
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
            # Sampler
            self.UI_sampler = QtGui.QComboBox()
            self.UI_sampler.addItems(sorted(self.samplers.keys()))
            self.UI_sampler.currentIndexChanged[str].connect(
                self.on_sampler_change
            )

            samplerT = self.addToolBar("Sampler")
            samplerT.pyqtConfigure(
                movable=False, objectName="Sampler",
                toolTip="The Sampler on which to run the Experiment."
            )
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            samplerT.addWidget(self.UI_sampler)

            # #threads
            self.UI_nthreads = QtGui.QComboBox()
            self.UI_nthreads.currentIndexChanged[str].connect(
                self.on_nthreads_change
            )

            nthreadsT = self.addToolBar("#threads")
            nthreadsT.pyqtConfigure(
                movable=False, objectName="#threads",
                toolTip="The number of threads for the kernel (BLAS) library."
                "\nCan be linked to the range variable."
            )
            nthreadsT.addWidget(QtGui.QLabel("#threads:"))
            nthreadsT.addWidget(self.UI_nthreads)

            # spacer
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
            # submit
            self.UI_reportname = QtGui.QLineEdit(
                textChanged=self.on_reportname_change,
                toolTip="Name for the Report."
            )
            self.UI_reportname.setFixedWidth(32)
            reportname_choose = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_FileDialogStart),
                "...", self, triggered=self.on_reportname_choose,
                toolTip="Browse Report folder."
            )
            self.UI_submit = QtGui.QAction(self.style().standardIcon(
                QtGui.QStyle.SP_DialogOkButton
            ), "Run", self, triggered=self.on_submit)

            submitT = self.addToolBar("Submit")
            submitT.pyqtConfigure(movable=False, objectName="Submit")
            submitT.addWidget(spacer)
            submitT.addWidget(QtGui.QLabel("Report name:"))
            submitT.addWidget(self.UI_reportname)
            submitT.addAction(reportname_choose)
            submitT.addAction(self.UI_submit)

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
                textEdited=self.on_rangevar_change,
                editingFinished=self.UI_range_set,
                toolTip="The variable that contains the range value.\n"
                "Can be used in any numeric field below and in #threads above."
            )
            self.UI_rangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_rangevar
            ))
            self.UI_rangevar.setFixedWidth(32)
            self.UI_rangevals = QtGui.QLineEdit(
                minimumWidth=32,
                textEdited=self.on_rangevals_change,
                editingFinished=self.UI_range_set,
                toolTip="Values for the range.\nSyntax: start:step:stop, a "
                "comma separated list of values, or a combination of both."
            )

            rangeL = QtGui.QHBoxLayout(spacing=0)
            rangeL.setContentsMargins(0, 0, 0, 0)
            rangeL.addWidget(QtGui.QLabel("for "))
            rangeL.addWidget(self.UI_rangevar)
            rangeL.addWidget(QtGui.QLabel(" = "))
            rangeL.addWidget(self.UI_rangevals)
            rangeL.addWidget(QtGui.QLabel(":"))
            rangeL.addStretch(1)
            self.UI_rangeW = QtGui.QWidget(
                toolTip="A range of values for which to perform the "
                "measurements.\n(x-axis in the Viewer)"
            )
            self.UI_rangeW.setLayout(rangeL)

            # reps
            self.UI_nreps = QtGui.QLineEdit(
                textEdited=self.on_nreps_change,
                editingFinished=self.UI_nreps_set,
                toolTip="The variable that contains the range value.\n"
                "Can be used in any numeric field below above."
            )
            # self.UI_nreps.setValidator(QtGui.QIntValidator(bottom=1))
            self.UI_nreps.setValidator(QtGui.QIntValidator(1, 1000000, self))
            self.UI_nreps.setFixedWidth(32)

            nrepsL = QtGui.QHBoxLayout(spacing=0)
            nrepsL.setContentsMargins(16, 4, 0, 0)
            nrepsL.addWidget(QtGui.QLabel("repeat "))
            nrepsL.addWidget(self.UI_nreps)
            nrepsL.addWidget(QtGui.QLabel(" times:"))
            nrepsL.addStretch(1)
            self.UI_nrepsW = QtGui.QWidget(
                toolTip="Number of repetitions for statistcal evaluation."
            )
            self.UI_nrepsW.setLayout(nrepsL)

            # sumrange
            self.UI_sumrange_parallel = QtGui.QComboBox(
                toolTip="sum over: the calls are executed sequencially and "
                "the measurements are summed to a single value.\n#omp for: "
                "the calls in the range are executed in parallel through "
                "OpenMP yielding one measurement value."
            )
            self.UI_sumrange_parallel.addItems(["sum over", "#omp for"])
            self.UI_sumrange_parallel.currentIndexChanged[int].connect(
                self.on_sumrange_parallel_change
            )
            self.UI_sumrangevar = QtGui.QLineEdit(
                textEdited=self.on_sumrangevar_change,
                editingFinished=self.UI_sumrange_set
            )
            self.UI_sumrangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_sumrangevar
            ))
            self.UI_sumrangevar.setFixedWidth(32)
            self.UI_sumrangevals = QtGui.QLineEdit(
                minimumWidth=32,
                textEdited=self.on_sumrangevals_change,
                editingFinished=self.UI_sumrange_set,
                toolTip="Values for the sum/omp range.\nSyntax: "
                "start:step:stop, a comma separated list of values, or a "
                "combination of both."
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
            self.UI_sumrangeW = QtGui.QWidget(
                toolTip="A range of values for which the performance is "
                "collected as a single value."
            )
            self.UI_sumrangeW.setLayout(sumrangeL)

            # calls_parallel
            calls_parallelL = QtGui.QHBoxLayout()
            calls_parallelL.setContentsMargins(48, 0, 0, 0)
            calls_parallelL.addWidget(QtGui.QLabel("in parallel:"))
            calls_parallelL.addStretch(1)
            self.UI_calls_parallelW = QtGui.QWidget(
                toolTip="Execute the calls below in parallel thorugh OpenMP."
            )
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
        self.reportname = str(settings.value("reportname", type=str))
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

    def UI_set_invalid(self, widget, state=True):
        """Set a widget's "invalid" property."""
        widget.setProperty("invalid", state)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    # Experiment routines
    def experiment_set(self, ex):
        """Insert own/new objects into loaded Experiment."""
        # own Sampler
        if ex.sampler is None or ex.sampler["name"] not in self.samplers:
            sampler = self.samplers[min(self.samplers)]
        else:
            sampler = self.samplers[ex.sampler["name"]]
        ex.set_sampler(sampler, force=True)

        # own Signatures
        newcalls = []
        for call in ex.calls:
            sig = self.sig_get(call[0])
            if sig:
                newcalls.append(sig(*call[1:]))
            else:
                newcalls.append(call)
        ex.calls = newcalls

        self.experiment = ex

    def experiment_reset(self):
        """Reset Experiment to default."""
        self.experiment_set(elaps.io.load_experiment_string(
            defines.default_experiment_str
        ))
        self.log("Loaded default Experiment")

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
        """Infer Ld and Lwork (if not showing)."""
        ex = self.experiment
        if signature.Ld in self.hideargs:
            ex.infer_lds(callid)
        if signature.Lwork in self.hideargs:
            ex.infer_lworks(callid)
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
                sig = elaps.io.load_signature(routine)
                sig()  # try the signature
                self.sigs[routine] = sig
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
        data = ex.get_operand(name)
        vary = ex.vary[name]

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
                "Vary with %s" % ex.sumrange_var, self,
                checkable=True, checked=ex.sumrange_var in vary["with"],
                toggled=self.on_vary_with_toggle
            )

            withsumrange.name = name
            withsumrange.with_ = ex.sumrange_var
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
        self.UI_hideargs_set()
        self.UI_reportname_set()
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

    def UI_reportname_set(self):
        """Set UI element: reportname."""
        self.UI_setting += 1
        self.UI_reportname.setText(self.reportname)
        self.UI_setting -= 1

    def UI_sampler_set(self):
        """Set UI element: Sampler."""
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
            self.UI_nthreads.addItem(str(self.experiment.range_var))
        self.UI_nthreads.setCurrentIndex(
            self.UI_nthreads.findText(str(self.experiment.nthreads))
        )
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_range_set(self):
        """Set UI element: range."""
        self.UI_setting += 1
        ex = self.experiment
        userange = bool(ex.range)
        self.UI_userange.setChecked(userange)
        self.UI_rangeW.setEnabled(userange)
        if userange:
            self.UI_rangevar.setText(str(ex.range_var))
            self.UI_set_invalid(self.UI_rangevar, False)
            self.UI_rangevals.setText(str(ex.range_vals))
            self.UI_set_invalid(self.UI_rangevals, False)
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_nreps_set(self):
        """Set UI element: nreps."""
        self.UI_setting += 1
        self.UI_nreps.setText(str(self.experiment.nreps))
        self.UI_set_invalid(self.UI_nreps, False)
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_sumrange_set(self):
        """Set UI element: sumrange."""
        self.UI_setting += 1
        ex = self.experiment
        usesumrange = bool(ex.sumrange)
        self.UI_usesumrange.setChecked(usesumrange)
        self.UI_sumrangeW.setEnabled(usesumrange)
        if usesumrange:
            self.UI_sumrange_parallel.setEnabled(ex.sampler["omp_enabled"])
            self.UI_sumrange_parallel.setCurrentIndex(int(ex.sumrange_parallel))
            self.UI_sumrangevar.setText(str(ex.sumrange_var))
            self.UI_set_invalid(self.UI_sumrangevar, False)
            self.UI_sumrangevals.setText(str(ex.sumrange_vals))
            self.UI_set_invalid(self.UI_sumrangevals, False)
        self.UI_setting -= 1

    def UI_calls_parallel_set(self):
        """Set UI element: calls_parallel."""
        self.UI_setting += 1
        ex = self.experiment
        calls_parallel = ex.calls_parallel
        self.UI_calls_parallel.setEnabled(ex.sampler["omp_enabled"])
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
        """Set UI element: counters."""
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
        settings.setValue("reportname", self.reportname)
        self.log("Experiment saved.")

    @pyqtSlot()
    def on_experiment_reset(self):
        """Event: reset Experiment."""
        self.experiment_reset()
        self.UI_setall()

    @pyqtSlot()
    def on_experiment_load(self, report=False):
        """Event: load Experiment."""
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Load Experiment",
            elaps.io.reportpath if report else defines.experimentpath,
            " ".join("*." + ext for ext in defines.experiment_extensions)
        )
        if not filename:
            return
        self.experiment_load(str(filename))
        self.UI_setall()

    @pyqtSlot()
    def on_experiment_load_report(self):
        """Event: load Experiment from Report."""
        self.on_experiment_load(True)

    @pyqtSlot()
    def on_experiment_save(self):
        """Event: save Experiment."""
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
    def on_reportname_change(self, value):
        """Event: change Report name."""
        value = str(value)
        sender = self.UI_reportname
        width = sender.fontMetrics().width(value) + 4
        width += sender.minimumSizeHint().width()
        margins = sender.getTextMargins()
        width += margins[0] + margins[2]
        width = min(width, sender.sizeHint().width())
        width = max(width, sender.sizeHint().height())
        sender.setFixedWidth(width)
        if self.UI_setting:
            return
        self.reportname = value

    @pyqtSlot()
    def on_reportname_choose(self):
        """Event: choose Report (file) name."""
        filebase = os.path.relpath(os.path.join(
            defines.reportpath, self.reportname
        ))
        filename = QtGui.QFileDialog.getSaveFileName(
            self, "Choose Report file", filebase,
            "Reports (*.%s)" % defines.report_extension,
            options=QtGui.QFileDialog.DontConfirmOverwrite
        )
        if not filename:
            return
        reportname = os.path.relpath(str(filename), defines.reportpath)
        if reportname[-4:] == "." + defines.report_extension:
            reportname = reportname[:-4]
        self.reportname = reportname
        self.UI_reportname_set()

    @pyqtSlot()
    def on_submit(self):
        """Event: submit."""
        reportname = str(self.UI_reportname.text())
        filebase = os.path.relpath(os.path.join(
            defines.reportpath, reportname
        ))
        self.experiment_submit(filebase)

    @pyqtSlot(str)
    def on_note_change(self):
        """Event: changed note."""
        if self.UI_setting:
            return
        self.experiment.note = self.UI_note.toPlainText()

    @pyqtSlot(str)
    def on_sampler_change(self, value, force=False):
        """Event: change Sampler."""
        if self.UI_setting:
            return
        try:
            sampler = self.samplers[str(value)]
            self.experiment.set_sampler(sampler, force=force)
            self.UI_setall()
        except Exception as e:
            self.UI_dialog(
                "question", "Incompatible Sampler",
                "Sampler %s is not compatible with the current Experiment\n"
                "(%s)\nAdjust the Experiment?" % (value, e),
                {"Ok": (self.on_sampler_change, (value, True)), "Cancel": None}
            )

    @pyqtSlot(str)
    def on_nthreads_change(self, value):
        """Event: change #threads."""
        if self.UI_setting:
            return
        self.experiment.set_nthreads(str(value), force=True)

    @pyqtSlot(bool)
    def on_userange_toggle(self, checked):
        """Event: change if range is used."""
        if self.UI_setting:
            return
        ex = self.experiment
        if checked:
            range_var = str(self.UI_rangevar.text())
            range_vals = str(self.UI_rangevals.text())
            ex.set_range((range_var, range_vals), force=True)
        else:
            ex.set_range(None)
            self.UI_sumrange_set()
        self.UI_nthreads_set()
        self.UI_range_set()
        self.UI_calls_set()
        self.UI_submit_setenabled()

    @pyqtSlot(str)
    def on_rangevar_change(self, value):
        """Event: change range variable."""
        try:
            self.experiment.set_range_var(str(value))
            self.UI_set_invalid(self.UI_rangevar, False)
            self.UI_nthreads_set()
            self.UI_sumrange_set()
            self.UI_calls_set()
            self.UI_submit_setenabled()
        except:
            self.UI_set_invalid(self.UI_rangevar)

    @pyqtSlot(str)
    def on_rangevals_change(self, value):
        """Event: change range."""
        try:
            self.experiment.set_range_vals(str(value))
            self.UI_set_invalid(self.UI_rangevals, False)
            self.experiment_infer_update_set()
        except:
            self.UI_set_invalid(self.UI_rangevals)

    @pyqtSlot(str)
    def on_nreps_change(self, value):
        """Event: change #repetitions."""
        try:
            self.experiment.set_nreps(str(value))
            self.UI_set_invalid(self.UI_nreps, False)
            self.experiment_infer_update_set()
        except:
            self.UI_set_invalid(self.UI_nreps)

    @pyqtSlot(bool)
    def on_usesumrange_toggle(self, checked):
        """Event: change if sumrange is used."""
        if self.UI_setting:
            return
        ex = self.experiment
        if checked:
            sumrange_var = str(self.UI_sumrangevar.text())
            sumrange_vals = str(self.UI_sumrangevals.text())
            sumrange_parallel = bool(int(
                self.UI_sumrange_parallel.currentIndex()
            ))
            ex.set_sumrange((sumrange_var, sumrange_vals), force=True)
            ex.set_sumrange_parallel(sumrange_parallel, force=True)
        else:
            ex.set_sumrange(None)
        self.UI_sumrange_set()
        self.UI_calls_set()
        self.UI_submit_setenabled()

    @pyqtSlot(int)
    def on_sumrange_parallel_change(self, value):
        """Event: change if sumrange is in parallel."""
        if self.UI_setting:
            return
        self.experiment.set_sumrange_parallel(bool(value))
        self.UI_sumrange_set()

    @pyqtSlot(str)
    def on_sumrangevar_change(self, value):
        """Event: change sumrange variable."""
        try:
            self.experiment.set_sumrange_var(str(value))
            self.UI_set_invalid(self.UI_sumrangevar, False)
            self.UI_calls_set()
            self.UI_submit_setenabled()
        except:
            self.UI_set_invalid(self.UI_sumrangevar)

    @pyqtSlot(str)
    def on_sumrangevals_change(self, value):
        """Event: change sumrange."""
        try:
            self.experiment.set_sumrange_vals(str(value))
            self.UI_set_invalid(self.UI_sumrangevals, False)
            self.experiment_infer_update_set()
        except:
            self.UI_set_invalid(self.UI_sumrangevals)

    @pyqtSlot(bool)
    def on_calls_parallel_toggle(self, value):
        """Event: change if calls are in parallel."""
        if self.UI_setting:
            return
        self.experiment.set_calls_parallel(bool(value))
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
        if value not in ex.sampler["kernels"]:
            self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0])
            return
        sig = self.sig_get(value)
        if not sig:
            try:
                # prepare call
                call = [value]

                # set call
                ex.set_call(callid, call)
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0],
                                    False)
                self.experiment_infer_update_set()
            except:
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0])
        else:
            try:
                # prepare call
                call = sig()
                operands = ex.operands
                varnames = [name for name in string.ascii_uppercase
                            if name not in operands]
                for argid, arg in enumerate(sig):
                    if isinstance(arg, (signature.Dim, signature.Ld)):
                        call[argid] = defines.default_dim
                    if isinstance(arg, signature.Data):
                        call[argid] = varnames.pop(0)

                # set call
                ex.set_call(callid, call, force=True)
                ex.infer_lds(callid)
                ex.infer_lworks(callid)
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0],
                                    False)
                self.experiment_infer_update_set()
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0])

    def on_arg_set(self, callid, argid, value):
        """Event: Set argument value."""
        if self.UI_setting:
            return
        if argid == 0:
            self.on_routine_set(callid, value)
            return
        try:
            self.experiment.set_arg(callid, argid, value)
            self.UI_set_invalid(self.UI_calls.item(callid).UI_args[argid],
                                False)
            self.experiment_infer_update_set()
        except Exception as e:
            if "Incompatible operand sizes" in str(e):
                ret = QtGui.QMessageBox.question(
                    self, str(e), "Adjust dimensions automatically?",
                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
                )
                if ret == QtGui.QMessageBox.Ok:
                    self.experiment.set_arg(callid, argid, value, force=True)
                    self.UI_set_invalid(
                        self.UI_calls.item(callid).UI_args[argid], False
                    )
                    self.experiment_infer_update_set()
                return
            self.UI_set_invalid(self.UI_calls.item(callid).UI_args[argid])
            if "Incompatible operand types:" in str(e):
                self.UI_alert(e)

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
        ex = self.experiment
        name = sender.name
        with_ = sender.with_
        if checked:
            ex.add_vary_with(name, with_)
        else:
            ex.remove_vary_with(name, with_)
        self.experiment_infer_update_set()

    # @pyqtSlot(bool)  # sender() pyqt bug
    def on_vary_along_toggle(self, checked):
        """Event: changed vary along."""
        sender = self.Qapp.sender()
        self.experiment.set_vary_along(sender.name, sender.along)
        self.experiment_infer_update_set()

    # @pyqtSlot()  # sender() pyqt bug
    def on_vary_offset(self):
        """Event: set vary offset."""
        sender = self.Qapp.sender()
        ex = self.experiment
        name = sender.name
        offset = ex.vary[name]["offset"]
        value, ok = QtGui.QInputDialog.getText(
            self, "Vary offset for %s" % name,
            "Vary offset for %s:" % name, text=str(offset)
        )
        if not ok:
            return
        value = str(value) or "0"
        try:
            ex.set_vary_offset(name, value)
            self.experiment_infer_update_set()
        except:
            self.UI_alert("Invalid offset:\n%s" % value)

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
        """Event: open Report in Viewer."""
        if not self.Qapp.viewer:
            self.viewer_start(filename)
            return
        self.Qapp.viewer.report_load(filename, UI_alert=True)
        self.Qapp.viewer.UI_setall()
        self.Qapp.viewer.show()
        self.Qapp.viewer.raise_()
