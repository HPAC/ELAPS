"""GUI for Experiments."""

from __future__ import print_function

import sys
import os
import string
import itertools

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot

import elaps
from elaps import defines
from elaps import signature
from elaps.experiment import Experiment
from elaps.qt.call import QCall
from elaps.qt.jobprogress import QJobProgress


class PlayMat(QtGui.QMainWindow):

    """GUI for Experiment."""

    def __init__(self, app=None, load=None, reset=False):
        """Initialize the PlayMat."""
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
        self.viz_scale = defines.viz_scale
        self.reportname_set()
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
            self.experiment_new()

        # undo stack
        self.undo_stack = []
        self.redo_stack = []

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

        # clipboard
        self.Qapp.clipboard().changed.connect(self.on_clipboard_change)

        def create_actions():
            """Create all actions."""
            # EXPERIMENT

            # print
            QtGui.QShortcut(
                QtGui.QKeySequence.Print, self, lambda: print(self.experiment)
            )

            # submit
            self.UIA_submit = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPlay),
                "Run Experiment", self,
                shortcut=QtGui.QKeySequence("Ctrl+R"),
                triggered=self.on_submit
            )

            # new
            self.UIA_new = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_FileIcon),
                "New Experiment", self,
                shortcut=QtGui.QKeySequence("Ctrl+Shift+N"),
                triggered=self.on_experiment_new
            )

            # load
            self.UIA_load = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton),
                "Load Experiment ...", self,
                shortcut=QtGui.QKeySequence.Open,
                triggered=self.on_experiment_load
            )
            # load report
            QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+O"), self,
                self.on_experiment_load_report
            )

            # save
            self.UIA_save = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton),
                "Save Experiment ...", self,
                shortcut=QtGui.QKeySequence.Save,
                triggered=self.on_experiment_save
            )

            # EDIT

            # undo
            self.UIA_undo = QtGui.QAction(
                "Undo", self, enabled=False,
                shortcut=QtGui.QKeySequence.Undo,
                triggered=self.on_undo
            )

            # redo
            self.UIA_redo = QtGui.QAction(
                "Redo", self, enabled=False,
                shortcut=QtGui.QKeySequence.Redo,
                triggered=self.on_redo
            )

            # CALLS

            # new
            self.UIA_call_new = QtGui.QAction(
                "New Call", self,
                shortcut=QtGui.QKeySequence.New,
                triggered=self.on_call_new
            )

            # delete
            self.UIA_call_delete = QtGui.QAction(
                "Delete Call(s)", self, enabled=False,
                shortcut=QtCore.Qt.Key_Backspace,
                triggered=self.on_call_delete
            )
            self.UIA_call_delete2 = QtGui.QAction(
                "Delete Call(s)", self, enabled=False,
                shortcut=QtGui.QKeySequence.Delete,
                triggered=self.on_call_delete
            )

            # cut
            self.UIA_call_cut = QtGui.QAction(
                "Cut Call(s)", self, enabled=False,
                shortcut=QtGui.QKeySequence.Cut,
                triggered=self.on_call_cut
            )

            # copy
            self.UIA_call_copy = QtGui.QAction(
                "Copy Call(s)", self, enabled=False,
                shortcut=QtGui.QKeySequence.Copy,
                triggered=self.on_call_copy
            )

            # paste
            self.UIA_call_paste = QtGui.QAction(
                "Paste Call(s)", self, enabled=False,
                shortcut=QtGui.QKeySequence.Paste,
                triggered=self.on_call_paste
            )

            # OPTIONS

            # hideargs
            self.UIA_hideargs = []
            for desc, classes in (
                ("hide flags", (signature.Flag,)),
                ("hide scalars", (signature.Scalar,)),
                ("hide leading dimensions", (signature.Ld, signature.Inc)),
                ("hide work spaces", (signature.Work, signature.Lwork)),
                ("hide infos", (signature.Info,))
            ):
                UIA_hidearg = QtGui.QAction(
                    desc, self, checkable=True,
                    toggled=self.on_hideargs_toggle
                )
                UIA_hidearg.classes = set(classes)
                self.UIA_hideargs.append(UIA_hidearg)

            # zoom
            self.UIA_zoom_in = QtGui.QAction(
                "Zoom in", self,
                shortcut=QtGui.QKeySequence.ZoomIn,
                triggered=self.on_zoom_in
            )
            self.UIA_zoom_out = QtGui.QAction(
                "Zoom out", self,
                shortcut=QtGui.QKeySequence.ZoomOut,
                triggered=self.on_zoom_out
            )

            # MISC

            # start viewer
            self.UIA_viewer_start = QtGui.QAction(
                "Start Viewer", self,
                triggered=self.on_viewer_start
            )

            # visit github
            self.UIA_visit_github = QtGui.QAction(
                "View ELAPS on GitHub", self,
                triggered=self.on_visit_github
            )

        def create_menus():
            """Create all menus."""
            menu = self.menuBar()

            # file
            self.UIM_file = menu.addMenu("File")
            self.UIM_file.addAction(self.UIA_submit)
            self.UIM_file.addSeparator()
            self.UIM_file.addAction(self.UIA_new)
            self.UIM_file.addAction(self.UIA_load)
            self.UIM_file.addAction(self.UIA_save)
            self.UIM_file.addSeparator()
            self.UIM_file.addAction(self.UIA_viewer_start)

            # edit
            self.UIM_edit = menu.addMenu("Edit")
            self.UIM_edit.addAction(self.UIA_undo)
            self.UIM_edit.addAction(self.UIA_redo)
            self.UIM_edit.addSeparator()
            self.UIM_edit.addAction(self.UIA_call_new)
            self.UIM_edit.addAction(self.UIA_call_cut)
            self.UIM_edit.addAction(self.UIA_call_copy)
            self.UIM_edit.addAction(self.UIA_call_paste)
            self.UIM_edit.addAction(self.UIA_call_delete)

            # view
            self.UIM_view = menu.addMenu("View")
            for UIA_hidearg in self.UIA_hideargs:
                self.UIM_view.addAction(UIA_hidearg)
            self.UIM_view.addAction(self.UIA_zoom_in)
            self.UIM_view.addAction(self.UIA_zoom_out)

            # help
            self.UIM_help = menu.addMenu("Help")
            self.UIM_help.addAction(self.UIA_visit_github)

            # CONTEXT MENUS

            # calls
            self.UIM_calls = QtGui.QMenu()
            self.UIM_calls.addAction(self.UIA_call_new)
            self.UIM_calls.addAction(self.UIA_call_cut)
            self.UIM_calls.addAction(self.UIA_call_copy)
            self.UIM_calls.addAction(self.UIA_call_paste)
            self.UIM_calls.addSeparator()
            self.UIM_calls.addMenu(self.UIM_view)

        def create_toolbars():
            """Create all toolbars."""
            # new/load/save experiment
            fileT = self.addToolBar("File")
            fileT.pyqtConfigure(movable=False, objectName="File")
            fileT.addAction(self.UIA_new)
            fileT.addAction(self.UIA_load)
            fileT.addAction(self.UIA_save)

            # spacer
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
            # submit
            self.UI_reportname = QtGui.QLineEdit(
                textChanged=self.on_reportname_change,
                returnPressed=self.on_submit,
                toolTip="Name for the Report."
            )
            reportname_choose = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton),
                "...", self,
                triggered=self.on_reportname_choose,
                toolTip="Browse Report folder."
            )

            submitT = self.addToolBar("Submit")
            submitT.pyqtConfigure(movable=False, objectName="Submit")
            submitT.addWidget(spacer)
            submitT.addWidget(QtGui.QLabel("Report name:"))
            submitT.addWidget(self.UI_reportname)
            submitT.addAction(reportname_choose)
            submitT.addAction(self.UIA_submit)

        def create_setup():
            """Create the ranges dock widget."""
            # sampler
            self.UI_sampler = QtGui.QComboBox(
                toolTip="<tt>sampler</tt>: "
                "The Sampler on which to run the Experiment."
            )
            self.UI_sampler.addItems(sorted(self.samplers.keys()))
            self.UI_sampler.currentIndexChanged[str].connect(
                self.on_sampler_change
            )

            samplerL = QtGui.QHBoxLayout(spacing=0)
            samplerL.setContentsMargins(0, 0, 0, 0)
            samplerL.addWidget(QtGui.QLabel("Sampler = "))
            samplerL.addWidget(self.UI_sampler)
            samplerL.addStretch(1)
            samplerW = QtGui.QWidget()
            samplerW.setLayout(samplerL)

            # range
            self.UI_userange = QtGui.QCheckBox(
                " ", toggled=self.on_userange_toggle
            )
            self.UI_rangevar = QtGui.QLineEdit(
                textEdited=self.on_rangevar_change,
                editingFinished=self.UI_range_set,
                toolTip="<tt>range_var</tt> (<tt>range[0]</tt>): "
                "The variable that contains the range value.\n"
                "Can be used in any numeric field below and in #threads above."
            )
            self.UI_rangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_rangevar
            ))
            self.UI_rangevals = QtGui.QLineEdit(
                minimumWidth=32,
                textEdited=self.on_rangevals_change,
                editingFinished=self.UI_range_set,
                toolTip="<tt>range_vals</tt> (<tt>range[1]</tt>): "
                "Values for the range.\nSyntax: <tt>start[[:step]:stop]</tt>, "
                "a comma separated list of values, or a combination of both."
            )

            # shuffle
            self.UI_shuffle = QtGui.QCheckBox(
                "shuffle reps",
                toggled=self.on_shuffle_toggle,
                toolTip="<tt>shuffle</tt>: "
                "range and repetition loops are interchanged."
            )

            rangeL = QtGui.QHBoxLayout(spacing=0)
            rangeL.setContentsMargins(0, 0, 0, 0)
            rangeL.addWidget(QtGui.QLabel("for "))
            rangeL.addWidget(self.UI_rangevar)
            rangeL.addWidget(QtGui.QLabel(" = "))
            rangeL.addWidget(self.UI_rangevals)
            rangeL.addWidget(QtGui.QLabel(": "))
            rangeL.addWidget(self.UI_shuffle)
            rangeL.addStretch(1)
            self.UI_rangeW = QtGui.QWidget(
                toolTip="<tt>range</tt>: "
                "A range of values for which to perform the measurements.\n"
                "(x-axis in the Viewer)"
            )
            self.UI_rangeW.setLayout(rangeL)

            # #threads
            self.UI_nthreads = QtGui.QLineEdit(
                textEdited=self.on_nthreads_change,
                editingFinished=self.UI_nthreads_set,
                toolTip="<tt>nthreads</tt>: "
                "The number of threads for the kernel (BLAS) library."
            )

            nthreadsL = QtGui.QHBoxLayout(spacing=0)
            nthreadsL.setContentsMargins(0, 0, 0, 0)
            nthreadsL.addWidget(QtGui.QLabel("#threads = "))
            nthreadsL.addWidget(self.UI_nthreads)
            nthreadsL.addStretch(1)
            self.UI_nthreadsW = QtGui.QWidget()
            self.UI_nthreadsW.setLayout(nthreadsL)

            # reps
            self.UI_nreps = QtGui.QLineEdit(
                textEdited=self.on_nreps_change,
                editingFinished=self.UI_nreps_set,
                toolTip="<tt>nreps</tt>: "
                "Number of repetitions for statistical evaluation."
            )

            nrepsL = QtGui.QHBoxLayout(spacing=0)
            nrepsL.setContentsMargins(0, 0, 0, 0)
            nrepsL.addWidget(QtGui.QLabel("repeat "))
            nrepsL.addWidget(self.UI_nreps)
            nrepsL.addWidget(QtGui.QLabel(" times:"))
            nrepsL.addStretch(1)
            self.UI_nrepsW = QtGui.QWidget()
            self.UI_nrepsW.setLayout(nrepsL)

            # sumrange
            self.UI_usesumrange = QtGui.QCheckBox(
                " ", toggled=self.on_usesumrange_toggle
            )
            self.UI_sumrange_parallel = QtGui.QComboBox(
                toolTip="<tt>sumrange_parallel</tt>:\n"
                "<i>sum over</i>: the calls are executed sequentially and "
                "the measurements are summed to a single value.\n"
                "<i>#omp for</i>: the calls in the range are executed in"
                "parallel through OpenMP yielding one measurement value."
            )
            self.UI_sumrange_parallel.addItems(["sum over", "#omp for"])
            self.UI_sumrange_parallel.currentIndexChanged[int].connect(
                self.on_sumrange_parallel_change
            )
            self.UI_sumrangevar = QtGui.QLineEdit(
                textEdited=self.on_sumrangevar_change,
                editingFinished=self.UI_sumrange_set,
                toolTip="<tt>sumrange_var</tt> (<tt>sumrange[0]</tt>): "
                "The variable that contains the sum/omp-range value."
            )
            self.UI_sumrangevar.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[a-zA-Z]+"), self.UI_sumrangevar
            ))
            self.UI_sumrangevals = QtGui.QLineEdit(
                minimumWidth=32,
                textEdited=self.on_sumrangevals_change,
                editingFinished=self.UI_sumrange_set,
                toolTip="<tt>sumrange_vals</tt> (<tt>sumrange[1]</tt>): "
                "Values for the range.\nSyntax: <tt>start:step:stop</tt>, a "
                "comma separated list of values, or a combination of both."
            )

            sumrangeL = QtGui.QHBoxLayout(spacing=0)
            sumrangeL.setContentsMargins(0, 0, 0, 0)
            sumrangeL.addWidget(self.UI_sumrange_parallel)
            sumrangeL.addWidget(QtGui.QLabel(" "))
            sumrangeL.addWidget(self.UI_sumrangevar)
            sumrangeL.addWidget(QtGui.QLabel(" = "))
            sumrangeL.addWidget(self.UI_sumrangevals)
            sumrangeL.addWidget(QtGui.QLabel(":"))
            sumrangeL.addStretch(1)
            self.UI_sumrangeW = QtGui.QWidget(
                toolTip="<tt>range</tt>: "
                "A range of values for which the performance is collected as a"
                "single data point."
            )
            self.UI_sumrangeW.setLayout(sumrangeL)

            # calls_parallel
            self.UI_calls_parallel = QtGui.QCheckBox(
                " ", toggled=self.on_calls_parallel_toggle
            )

            calls_parallelL = QtGui.QHBoxLayout()
            calls_parallelL.setContentsMargins(0, 0, 0, 0)
            calls_parallelL.addWidget(QtGui.QLabel("in parallel:"))
            calls_parallelL.addStretch(1)
            self.UI_calls_parallelW = QtGui.QWidget(
                toolTip="<tt>calls_parallel</tt>: "
                "Execute the calls below in parallel through OpenMP."
            )
            self.UI_calls_parallelW.setLayout(calls_parallelL)

            setupL = QtGui.QGridLayout(spacing=0)
            for col in range(6):
                setupL.setColumnMinimumWidth(col, 8)
            setupL.addWidget(samplerW,
                             0, 0, 1, 8)
            setupL.addWidget(self.UI_userange,
                             1, 0, 1, 2)
            setupL.addWidget(self.UI_rangeW,
                             1, 2, 1, 6)
            setupL.addWidget(QtGui.QFrame(frameShape=QtGui.QFrame.VLine),
                             2, 1, 4, 1)
            setupL.addWidget(self.UI_nthreadsW,
                             2, 2, 1, 6)
            setupL.addWidget(self.UI_nrepsW,
                             3, 2, 1, 6)
            setupL.addWidget(QtGui.QFrame(frameShape=QtGui.QFrame.VLine),
                             4, 3, 2, 1)
            setupL.addWidget(self.UI_usesumrange,
                             4, 4, 1, 2)
            setupL.addWidget(self.UI_sumrangeW,
                             4, 6, 1, 4)
            setupL.addWidget(QtGui.QFrame(frameShape=QtGui.QFrame.VLine),
                             5, 5, 1, 1)
            setupL.addWidget(self.UI_calls_parallel,
                             5, 6, 1, 1)
            setupL.addWidget(self.UI_calls_parallelW,
                             5, 7, 1, 1)

            setupW = QtGui.QWidget()
            setupW.setLayout(setupL)

            setupD = QtGui.QDockWidget(
                "Sampler && Ranges", objectName="Setup",
                features=QtGui.QDockWidget.DockWidgetVerticalTitleBar,
            )
            setupD.setWidget(setupW)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, setupD)

        def create_note():
            """Create the note input."""
            self.UI_note = QtGui.QTextEdit(
                textChanged=self.on_note_change,
                toolTip="<tt>note</tt>: "
                "Comment field for the experiment."
            )

            noteD = QtGui.QDockWidget(
                "Note", objectName="Note",
                features=(QtGui.QDockWidget.DockWidgetVerticalTitleBar |
                          QtGui.QDockWidget.DockWidgetMovable)
            )
            noteD.setWidget(self.UI_note)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, noteD)

        def create_counters():
            """Create the counters widget."""
            countersW = QtGui.QWidget()
            countersW.setLayout(QtGui.QVBoxLayout())
            countersW.layout().insertStretch(100, 1)

            self.UI_countersD = QtGui.QDockWidget(
                "PAPI counters", objectName="PAPI counters",
                features=(QtGui.QDockWidget.DockWidgetVerticalTitleBar |
                          QtGui.QDockWidget.DockWidgetMovable),
                toolTip="<tt>papi_counters</tt>: "
                "List of counters to be measured through PAPI."
            )
            self.UI_countersD.setWidget(countersW)

            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.UI_countersD)
            self.UI_countersD.hide()

            self.UI_countersD.widgets = []

        def create_calls():
            """Create the calls list and add button (central widget)."""
            self.UI_calls = QtGui.QListWidget(
                verticalScrollMode=QtGui.QListWidget.ScrollPerPixel,
                selectionMode=QtGui.QListWidget.ExtendedSelection,
                dragDropMode=QtGui.QListWidget.InternalMove,
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                customContextMenuRequested=self.on_calls_rightclick,
                itemSelectionChanged=self.on_calls_selection_change,
                toolTip="<tt>calls</tt>: "
                "The list of calls to be measured."
            )
            self.UI_calls.model().layoutChanged.connect(self.on_calls_reorder)
            self.setCentralWidget(self.UI_calls)

            # actions
            self.UI_calls.addAction(self.UIA_call_new)
            self.UI_calls.addAction(self.UIA_call_delete)
            self.UI_calls.addAction(self.UIA_call_delete2)
            self.UI_calls.addAction(self.UIA_call_copy)
            self.UI_calls.addAction(self.UIA_call_cut)
            self.UI_calls.addAction(self.UIA_call_paste)

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

        create_actions()
        create_menus()
        create_toolbars()
        create_setup()
        create_note()
        create_counters()
        create_calls()
        create_style()

        self.UI_jobprogress = QJobProgress(self)

        self.show()

        self.UI_setting -= 1

    def UI_settings_load(self):
        """Load Qt settings."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        self.hideargs = eval(str(settings.value("hideargs", type=str)),
                             signature.__dict__)
        self.reportname_set(str(settings.value("reportname", type=str)))
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
        print("PlayMat:", msg)

    def alert(self, *args):
        """Log a message to stderr and statusbar."""
        msg = " ".join(map(str, args))
        self.statusBar().showMessage(msg)
        print("PlayMat:", "\033[31m%s\033[0m" % msg, file=sys.stderr)

    def UI_set_invalid(self, widget, state=True):
        """Set a widget's "invalid" property."""
        widget.setProperty("invalid", state)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def UI_edit_autowidth(self, widget, ratio=1):
        """Set a LineEdit's width according to the content."""
        value = str(widget.text())
        width = widget.fontMetrics().width(value) + 4
        width += widget.minimumSizeHint().width()
        margins = widget.getTextMargins()
        width += margins[0] + margins[2]
        width = min(width, widget.sizeHint().width())
        width = max(width, widget.sizeHint().height() * ratio)
        widget.setFixedWidth(width)

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
            sig = elaps.io.load_signature(call[0])
            if sig:
                newcalls.append(sig(*call[1:]))
            else:
                newcalls.append(call)
        ex.calls = newcalls

        self.experiment = ex

    def experiment_new(self):
        """Reset Experiment."""
        self.experiment_set(Experiment())
        self.reportname_set()
        self.experiment.calls.append([""])
        self.log("Reset Experiment")

    def experiment_qt_load(self):
        """Load Experiment from Qt setting."""
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        self.experiment_set(elaps.io.load_experiment_string(str(
            settings.value("Experiment", type=str)
        )))
        self.reportname_set(str(settings.value("reportname", type=str)))
        self.log("Loaded last Experiment")

    def experiment_load(self, filename):
        """Load Experiment from a file."""
        ex = elaps.io.load_experiment(filename)
        self.experiment_set(ex)
        self.reportname_set(filename=filename)
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
        filename = "%s.%s" % (filebase, defines.report_extension)
        self.log("Submitted job for %r to %r." % (filename, backend.name))

    def reportname_set(self, name=None, filename=None):
        """Set the reporname from a filename."""
        if name is not None:
            self.reportname = name
        elif filename:
            name = os.path.relpath(str(filename), defines.reportpath)
            if name[-4:] == "." + defines.report_extension:
                name = name[:-4]
            self.reportname = name
        else:
            self.reportname = defines.default_reportname
            i = 0
            while os.path.exists(os.path.join(defines.reportpath, "%s.%s" %
                                              (self.reportname,
                                               defines.report_extension))):
                i += 1
                self.reportname = defines.default_reportname + str(i)

        self.UI_reportname_set()

    # viewer
    def viewer_start(self, *args):
        """Start the Viewer."""
        from viewer import Viewer
        Viewer(*args, app=self.Qapp)

    # undo / redo
    def undo_stack_push(self):
        """Push current Experiment to undo stack."""
        self.undo_stack.append(self.experiment.copy())
        self.UIA_undo.setEnabled(True)

    def undo_stack_pop(self):
        """Pop Experiment from undo stack."""
        self.UIA_undo.setEnabled(len(self.undo_stack) > 1)
        return self.undo_stack.pop()

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
                    text, self, checkable=True,
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
            text, self,
            triggered=self.on_vary_offset
        )
        offset.name = name
        actions.append(offset)

        actions.append(None)

        return actions

    # UI setters
    def UI_setall(self, force=False):
        """Set all UI elements."""
        self.UI_hideargs_set()
        self.UI_reportname_set()
        self.UI_sampler_set()
        self.UI_nthreads_set()
        self.UI_range_set()
        self.UI_shuffle_set()
        self.UI_nreps_set()
        self.UI_sumrange_set()
        self.UI_calls_parallel_set()
        self.UI_submit_setenabled()
        self.UI_note_set()
        self.UI_counters_set()
        self.UI_calls_set(force)

    def UI_hideargs_set(self):
        """Set UI element: hideargs options."""
        self.UI_setting += 1
        for UIA_hidearg in self.UIA_hideargs:
            UIA_hidearg.setChecked(self.hideargs >= UIA_hidearg.classes)
        self.UI_setting -= 1

    def UI_reportname_set(self):
        """Set UI element: reportname."""
        self.UI_setting += 1
        if not self.UI_reportname.hasFocus():
            self.UI_reportname.setText(self.reportname)
        self.UI_set_invalid(self.UI_reportname, self.reportname == "")
        self.UI_setting -= 1

    def UI_sampler_set(self):
        """Set UI element: Sampler."""
        self.UI_setting += 1
        self.UI_sampler.setCurrentIndex(
            self.UI_sampler.findText(self.experiment.sampler["name"])
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
            self.UI_rangevals.setText(str(ex.range_vals))
        self.UI_edit_autowidth(self.UI_rangevar)
        self.UI_set_invalid(self.UI_rangevar, False)
        self.UI_edit_autowidth(self.UI_rangevals, 2)
        self.UI_set_invalid(self.UI_rangevals, False)
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_shuffle_set(self):
        """Set UI element: shuffle."""
        self.UI_setting += 1
        ex = self.experiment
        self.UI_shuffle.setEnabled(
            not ex.range or
            isinstance(ex.nthreads, int) and isinstance(ex.nreps, int)
        )
        self.UI_shuffle.setChecked(ex.shuffle)
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_nthreads_set(self):
        """Set UI element: #threads."""
        self.UI_setting += 1
        self.UI_nthreads.setText(str(self.experiment.nthreads))
        self.UI_edit_autowidth(self.UI_nthreads)
        self.UI_set_invalid(self.UI_nthreads, False)
        self.UI_setting -= 1

    @pyqtSlot()
    def UI_nreps_set(self):
        """Set UI element: nreps."""
        self.UI_setting += 1
        self.UI_nreps.setText(str(self.experiment.nreps))
        self.UI_edit_autowidth(self.UI_nreps)
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
            self.UI_sumrange_parallel.setCurrentIndex(
                int(ex.sumrange_parallel)
            )
            self.UI_sumrangevar.setText(str(ex.sumrange_var))
            self.UI_sumrangevals.setText(str(ex.sumrange_vals))
        self.UI_edit_autowidth(self.UI_sumrangevar)
        self.UI_set_invalid(self.UI_sumrangevar, False)
        self.UI_edit_autowidth(self.UI_sumrangevals, 2)
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

    def UI_calls_set(self, force=False):
        """Set UI element: calls."""
        self.UI_setting += 1
        for callid, call in enumerate(self.experiment.calls):
            if callid >= self.UI_calls.count():
                UI_call = QCall(self, callid)
                self.UI_calls.addItem(UI_call)
                self.UI_calls.setItemWidget(UI_call, UI_call.widget)
            self.UI_calls.item(callid).setall(force)
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
            if not self.reportname:
                raise Exception("empty report name")
            enabled = True
            tooltip = "Run"
        except Exception as e:
            enabled = False
            tooltip = str(e)
        self.UIA_submit.setEnabled(enabled)
        self.UIA_submit.setToolTip(tooltip)

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

    @pyqtSlot(QtGui.QClipboard.Mode)
    def on_clipboard_change(self, mode):
        """Event: clipboard changed."""
        if mode == QtGui.QClipboard.Clipboard:
            try:
                eval(str(self.Qapp.clipboard().text()), signature.__dict__)
                self.UIA_call_paste.setEnabled(True)
            except:
                self.UIA_call_paste.setEnabled(False)

    @pyqtSlot()
    def on_visit_github(self):
        """Event: visit GitHub."""
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(defines.github_url))

    @pyqtSlot()
    def on_undo(self):
        """Event: undo."""
        self.redo_stack.append(self.experiment.copy())
        self.UIA_redo.setEnabled(True)
        self.experiment = self.undo_stack_pop()
        self.UI_setall(True)

    @pyqtSlot()
    def on_redo(self):
        """Event: undo."""
        self.undo_stack_push()
        self.experiment = self.redo_stack.pop()
        self.UIA_redo.setEnabled(bool(self.redo_stack))
        self.UI_setall(True)

    @pyqtSlot()
    def on_experiment_new(self):
        """Event: reset Experiment."""
        self.undo_stack_push()
        self.experiment_new()
        self.UI_setall(True)

    @pyqtSlot()
    def on_experiment_load(self, report=False):
        """Event: load Experiment."""
        self.undo_stack_push()
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Load Experiment",
            defines.reportpath if report else defines.experimentpath,
            " ".join("*." + ext for ext in defines.experiment_extensions)
        )
        if not filename:
            return
        self.experiment_load(str(filename))
        self.UI_setall(True)

    @pyqtSlot()
    def on_experiment_load_report(self):
        """Event: load Experiment from Report."""
        self.on_experiment_load(True)

    @pyqtSlot()
    def on_experiment_save(self):
        """Event: save Experiment."""
        filename = QtGui.QFileDialog.getSaveFileName(
            self, "Save Setup", defines.experimentpath,
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

    @pyqtSlot()
    def on_zoom_in(self):
        """Event: Zoom in."""
        self.viz_scale *= 1.5
        self.UI_calls_set()

    @pyqtSlot()
    def on_zoom_out(self):
        """Event: Zoom out."""
        self.viz_scale /= 1.5
        self.UI_calls_set()

    @pyqtSlot(str)
    def on_reportname_change(self, value):
        """Event: change Report name."""
        self.UI_edit_autowidth(self.UI_reportname, 2)
        if self.UI_setting:
            return
        self.reportname_set(str(value))
        self.UI_submit_setenabled()

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
        self.reportname_set(filename=str(filename))
        self.UI_reportname_set()

    @pyqtSlot()
    def on_submit(self):
        """Event: submit."""
        filebase = os.path.relpath(os.path.join(
            defines.reportpath, self.reportname
        ))
        self.experiment_submit(filebase)

    @pyqtSlot(str)
    def on_note_change(self):
        """Event: changed note."""
        if self.UI_setting:
            return
        self.undo_stack_push()
        self.experiment.note = str(self.UI_note.toPlainText())

    @pyqtSlot(str)
    def on_sampler_change(self, value, force=False):
        """Event: change Sampler."""
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            sampler = self.samplers[str(value)]
            self.experiment.set_sampler(sampler, force=force)
            self.UI_setall()
        except Exception as e:
            self.undo_stack_pop()
            self.UI_dialog(
                "question", "Incompatible Sampler",
                "Sampler %s is not compatible with the current Experiment\n"
                "(%s)\nAdjust the Experiment?" % (value, e),
                {"Ok": (self.on_sampler_change, (value, True)), "Cancel": None}
            )

    @pyqtSlot(bool)
    def on_userange_toggle(self, checked):
        """Event: change if range is used."""
        if self.UI_setting:
            return
        self.undo_stack_push()
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
        self.UI_edit_autowidth(self.UI_rangevar)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_range_var(str(value))
            self.UI_set_invalid(self.UI_rangevar, False)
            self.UI_nthreads_set()
            self.UI_sumrange_set()
            self.UI_calls_set()
            self.UI_submit_setenabled()
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_rangevar)

    @pyqtSlot(str)
    def on_rangevals_change(self, value):
        """Event: change range."""
        self.UI_edit_autowidth(self.UI_rangevals, 2)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_range_vals(str(value))
            self.UI_set_invalid(self.UI_rangevals, False)
            self.experiment_infer_update_set()
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_rangevals)

    @pyqtSlot(str)
    def on_nthreads_change(self, value):
        """Event: change #threads."""
        self.UI_edit_autowidth(self.UI_nthreads)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_nthreads(str(value))
            self.UI_set_invalid(self.UI_nthreads, False)
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_nthreads)
        self.UI_shuffle_set()

    @pyqtSlot(str)
    def on_nreps_change(self, value):
        """Event: change #threads."""
        self.UI_edit_autowidth(self.UI_nreps)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_nreps(str(value))
            self.UI_set_invalid(self.UI_nreps, False)
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_nreps)
        self.UI_shuffle_set()

    @pyqtSlot(bool)
    def on_shuffle_toggle(self, checked):
        """Event: change shuffling."""
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_shuffle(bool(checked))
        except:
            self.undo_stack_pop()

    @pyqtSlot(bool)
    def on_usesumrange_toggle(self, checked):
        """Event: change if sumrange is used."""
        if self.UI_setting:
            return
        self.undo_stack_push()
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
        self.undo_stack_push()
        self.experiment.set_sumrange_parallel(bool(value))
        self.UI_sumrange_set()

    @pyqtSlot(str)
    def on_sumrangevar_change(self, value):
        """Event: change sumrange variable."""
        self.UI_edit_autowidth(self.UI_sumrangevar)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_sumrange_var(str(value))
            self.UI_set_invalid(self.UI_sumrangevar, False)
            self.UI_calls_set()
            self.UI_submit_setenabled()
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_sumrangevar)

    @pyqtSlot(str)
    def on_sumrangevals_change(self, value):
        """Event: change sumrange."""
        self.UI_edit_autowidth(self.UI_sumrangevals, 2)
        if self.UI_setting:
            return
        self.undo_stack_push()
        try:
            self.experiment.set_sumrange_vals(str(value))
            self.UI_set_invalid(self.UI_sumrangevals, False)
            self.experiment_infer_update_set()
        except:
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_sumrangevals)

    @pyqtSlot(bool)
    def on_calls_parallel_toggle(self, value):
        """Event: change if calls are in parallel."""
        if self.UI_setting:
            return
        self.undo_stack_push()
        self.experiment.set_calls_parallel(bool(value))
        self.UI_calls_parallel_set()

    @pyqtSlot()
    def on_calls_selection_change(self):
        """Event: call selection changed."""
        enabled = bool(self.UI_calls.selectedItems())
        self.UIA_call_delete.setEnabled(enabled)
        self.UIA_call_delete2.setEnabled(enabled)
        self.UIA_call_cut.setEnabled(enabled)
        self.UIA_call_copy.setEnabled(enabled)

    @pyqtSlot()
    def on_calls_reorder(self):
        """Event: change call order."""
        self.undo_stack_push()
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
        self.undo_stack_push()
        try:
            sig = elaps.io.load_signature(value)
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
                self.undo_stack_pop()
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0])
        except:
            try:
                # prepare call
                call = [value]

                # set call
                ex.set_call(callid, call)
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0],
                                    False)
                self.experiment_infer_update_set()
            except:
                self.undo_stack_pop()
                self.UI_set_invalid(self.UI_calls.item(callid).UI_args[0])

    def on_arg_set(self, callid, argid, value):
        """Event: Set argument value."""
        if self.UI_setting:
            return
        if argid == 0:
            self.on_routine_set(callid, value)
            return
        self.undo_stack_push()
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
                else:
                    self.undo_stack_pop()
                return
            self.undo_stack_pop()
            self.UI_set_invalid(self.UI_calls.item(callid).UI_args[argid])
            if "Incompatible operand types:" in str(e):
                self.UI_alert(e)

    @pyqtSlot(QtCore.QPoint)
    def on_calls_rightclick(self, pos):
        """Event: right click in calls."""
        globalpos = self.UI_calls.viewport().mapToGlobal(pos)
        self.UIM_calls.exec_(globalpos)

    @pyqtSlot()
    def on_call_new(self):
        """Event: new call."""
        self.undo_stack_push()
        callid = self.UI_calls.currentRow()
        if callid == -1:
            callid = len(self.experiment.calls)
        else:
            callid += 1
        self.experiment.calls.insert(callid, [""])
        self.UI_submit_setenabled()
        self.UI_calls_set()
        # focus on routine name of new call
        self.UI_calls.item(callid).UI_args[0].setFocus()

    @pyqtSlot()
    def on_call_delete(self):
        """Event: delete call(s)."""
        self.undo_stack_push()
        map(self.experiment.calls.pop,
            sorted(map(self.UI_calls.row, self.UI_calls.selectedItems()),
                   reverse=True))
        self.UI_submit_setenabled()
        self.UI_calls_set()

    @pyqtSlot()
    def on_call_cut(self):
        """Event: cut call(s)."""
        self.on_call_copy()
        self.on_call_delete()

    @pyqtSlot()
    def on_call_copy(self):
        """Event: copy call(s)."""
        selected_calls = [self.experiment.calls[callid] for callid in
                          map(self.UI_calls.row,
                              self.UI_calls.selectedItems())]
        self.Qapp.clipboard().setText(repr(selected_calls))

    @pyqtSlot()
    def on_call_paste(self):
        """Event: paste call(s)."""
        self.undo_stack_push()
        paste_calls = eval(str(self.Qapp.clipboard().text()),
                           signature.__dict__)
        callid = self.UI_calls.currentRow()
        calls = self.experiment.calls
        calls = calls[:callid] + paste_calls + calls[callid:]
        self.experiment.calls = calls
        self.UI_submit_setenabled()
        self.UI_calls_set()

    def on_infer_ld(self, callid, argid):
        """Event: infer ld."""
        self.undo_stack_push()
        self.experiment.infer_ld(callid, argid)
        self.UI_submit_setenabled()
        self.UI_calls_set()

    @pyqtSlot()
    def on_infer_lwork(self, callid, argid):
        """Event: infer lwork."""
        self.undo_stack_push()
        self.experiment.infer_lwork(callid, argid)
        self.UI_submit_setenabled()
        self.UI_calls_set()

    # @pyqtSlot(bool)  # sender() pyqt bug
    def on_vary_with_toggle(self, checked):
        """Event: changed vary with."""
        self.undo_stack_push()
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
        self.undo_stack_push()
        sender = self.Qapp.sender()
        self.experiment.set_vary_along(sender.name, sender.along)
        self.experiment_infer_update_set()

    # @pyqtSlot()  # sender() pyqt bug
    def on_vary_offset(self):
        """Event: set vary offset."""
        self.undo_stack_push()
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
        self.undo_stack_push()
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
