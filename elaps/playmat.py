#!/usr/bin/env python
"""GUI for Experiments."""
from __future__ import division, print_function

import elapsio
from experiment import Experiment
import symbolic

import sys
import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot


class PlayMat(object):

    """GUI for Experiment."""

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

        self.UI_init()

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
            self.experiment_load(os.path.join(elapsio.setuppath, "default.ees"))
        self.experiment_back = Experiment(self.experiment)
        self.UI_setall()
        if not reset:
            self.UI_settings_load()

    def UI_init(self):
        """Initialize all GUI elements."""
        self.UI_setting = 1

        # window
        window = self.UI_window = QtGui.QMainWindow()
        window.setWindowTitle("ELAPS:PlayMat")
        window.setUnifiedTitleAndToolBarOnMac(True)
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
            self.UI_submitA = QtGui.QAction("Run", window,
                                            triggered=self.on_submit)
            fileM.addAction(self.UI_submitA)
            self.UI_submitA.setShortcut(QtGui.QKeySequence("Ctrl+R"))

            # file
            fileM.addSeparator()

            # file > reset
            reset = QtGui.QAction("Reset Experiment", window,
                                  triggered=self.on_experiment_reset)
            fileM.addAction(reset)

            # file > load
            load = QtGui.QAction("Load Experiment ...", window,
                                 triggered=self.on_experiment_load)
            fileM.addAction(load)
            load.setShortcut(QtGui.QKeySequence.Open)

            # load report shortcut
            loadreport = QtGui.QShortcut(
                QtGui.QKeySequence("Ctrl+Shift+O"),
                window, self.on_experiment_load_report
            )

            # fie > save
            save = QtGui.QAction("Save Experiment ...", window,
                                 triggered=self.on_experiment_save)
            fileM.addAction(save)
            save.setShortcut(QtGui.QKeySequence.Save)

            # file
            fileM.addSeparator()

            viewer = QtGui.QAction("Start Viewer", window,
                                   triggered=self.on_viewer_start)
            fileM.addAction(viewer)

        def create_sampler():
            """Create the sampler Toolbar."""
            self.UI_sampler = QtGui.QComboBox()
            self.UI_sampler.addItems(sorted(self.samplers.keys()))
            self.UI_sampler.currentIndexChanged[str].connect(
                self.on_sampler_change
            )

            samplerT = window.addToolBar("Sampler")
            samplerT.setMovable(False)
            samplerT.setObjectName("Sampler")
            samplerT.addWidget(QtGui.QLabel("Sampler:"))
            samplerT.addWidget(self.UI_sampler)

        def create_nthreads():
            """Create the #threads toolbar."""
            self.UI_nthreads = QtGui.QComboBox()
            self.UI_nthreads.currentIndexChanged[str].connect(
                self.on_nthreads_change
            )

            nthreadsT = window.addToolBar("#threads")
            nthreadsT.setMovable(False)
            nthreadsT.setObjectName("#threads")
            nthreadsT.addWidget(QtGui.QLabel("#threads:"))
            nthreadsT.addWidget(self.UI_nthreads)

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
            self.UI_submit = QtGui.QAction(window.style().standardIcon(
                QtGui.QStyle.SP_DialogOkButton
            ), "Run", window, triggered=self.on_submit)
            samplerT.addAction(self.UI_submit)

        def create_ranges():
            """Create the ranges dock widget."""
            # checkboxes
            self.UI_userange = QtGui.QCheckBox(
                " ", stateChanged=self.on_userange_change
            )

            self.UI_usesumrange = QtGui.QCheckBox(
                " ", stateChanged=self.on_usesumrange_change
            )

            self.UI_calls_parallel = QtGui.QCheckBox(
                " ", stateChanged=self.on_calls_parallel_change
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

            rangeL = QtGui.QHBoxLayout()
            rangeL.setContentsMargins(0, 0, 0, 0)
            rangeL.setSpacing(0)
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
            self.UI_nreps.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp("[1-9][0-9]*"), self.UI_nreps
            ))
            self.UI_nreps.setFixedWidth(32)

            nrepsL = QtGui.QHBoxLayout()
            nrepsL.setContentsMargins(16, 4, 0, 0)
            nrepsL.setSpacing(0)
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

            sumrangeL = QtGui.QHBoxLayout()
            sumrangeL.setSpacing(0)
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

            rangesL = QtGui.QGridLayout()
            rangesL.setSpacing(0)
            rangesL.addWidget(self.UI_userange, 0, 0)
            rangesL.addWidget(self.UI_rangeW, 0, 1)
            rangesL.addWidget(self.UI_nrepsW, 1, 1)
            rangesL.addWidget(self.UI_usesumrange, 2, 0)
            rangesL.addWidget(self.UI_sumrangeW, 2, 1)
            rangesL.addWidget(self.UI_calls_parallel, 3, 0)
            rangesL.addWidget(self.UI_calls_parallelW, 3, 1)

            rangesW = QtGui.QWidget()
            rangesW.setLayout(rangesL)

            rangesD = QtGui.QDockWidget("Ranges")
            rangesD.setObjectName("Ranges")
            rangesD.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar)
            rangesD.setWidget(rangesW)

            window.addDockWidget(QtCore.Qt.TopDockWidgetArea, rangesD)

        def create_calls():
            """Create the calls list and add button (central widget)."""
            self.UI_calls = QtGui.QListWidget()
            self.UI_calls.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
            self.UI_calls.model().layoutChanged.connect(self.on_calls_reorder)
            self.UI_calls.focusOutEvent = self.on_calls_focusout

            window.setCentralWidget(self.UI_calls)

            # TODO: context menu

        def create_jobprogress():
            """Create the job pgoress dock widget."""
            jobprogressL = QtGui.QGridLayout()

            jobprogress = QtGui.QWidget()
            jobprogress.setSizePolicy(
                QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
            )
            jobprogress.setLayout(jobprogressL)

            self.UI_jobprogressD = QtGui.QDockWidget("Job Progress")
            self.UI_jobprogressD.setObjectName("Job Progress")
            self.UI_jobprogressD.setWidget(jobprogress)

            window.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                                 self.UI_jobprogressD)
            self.UI_jobprogressD.hide()

            self.UI_jobprogress_jobs = {}

            # timer
            self.jobprogress_timer = QtCore.QTimer(
                timeout=self.on_jobprogress_timer
            )
            self.jobprogress_timer.setInterval(1000)

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
        settings = QtCore.QSettings("HPAC", "ELAPS:PlayMat")
        exvalue = str(settings.value("Experiment").toString())
        elapsio.load_experiment_string(exvalue)
        ex = elapsio.load_experiment_string(exvalue)
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

    # loader routines
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
        if routine not in self.sigs:
            try:
                self.docs[routine] = elapsio.load_docs(routine)
                self.log("Loaded documentation for %r." % routine)
            except:
                self.docs[routine] = None
                self.log("Can't load documentation for %r." % routine)
        return self.docs[routine]

    # UI setters
    def UI_setall(self):
        """Set all UI elements."""
        # sampler
        self.UI_sampler_set()
        self.UI_nthreads_set()
        self.UI_range_set()
        self.UI_nreps_set()
        self.UI_sumrange_set()
        self.UI_calls_parallel_set()

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
        settings.setValue("Experiment", QtCore.QVariant(repr(self.experiment)))
        self.log("Experiment saved.")

    @pyqtSlot()
    def on_submit(self):
        """Event: submit."""
        # TODO

    @pyqtSlot()
    def on_experiment_reset(self):
        """Event: reset experiment."""
        self.experiment_reset()
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
            self.load_experiment(str(filename))

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
            "*.ems"
        )
        if filename:
            with open(str(filename), "w") as fout:
                fout.write(repr(self.experiment))

    @pyqtSlot()
    def on_viewer_start(self):
        """Event: start Viewer."""
        # TODO

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

    @pyqtSlot(int)
    def on_userange_change(self, value):
        """Event: change if range is used."""
        if self.UI_setting:
            return
        if value:
            if self.experiment_back.range:
                var, range_ = self.experiment_back.range
            else:
                var, range_ = "i", symbolic.Range((1, 1, 1,))
            if (self.experiment.sumrange and
                    self.experiment.sumrange[0] == var):
                var = "j" if self.experiment.sumrange[0] == "i" else "i"
            self.experiment.range = [var, range_]
        else:
            self.experiment_back.range = self.experiment.range
            # TODO: remove elsewhere
            self.experiment.range = None
        self.UI_range_set()

    @pyqtSlot(str)
    def on_rangevar_change(self, value):
        """Event: change range variable."""
        if self.UI_setting:
            return
        value = str(value)
        # TODO: check if == sumrange[0]
        if value:
            # TODO: change elsewhere
            self.experiment.range[0] = value
        else:
            # TODO: invalid
            pass

    @pyqtSlot(str)
    def on_rangevals_change(self, value):
        """Event: change range."""
        if self.UI_setting:
            return
        self.experiment.range[1] = symbolic.Range(str(value))

    @pyqtSlot(str)
    def on_nreps_change(self, value):
        """Event: change #repetitions."""
        if self.UI_setting:
            return
        value = str(value)
        if value:
            self.experiment.nreps = int(value)

    @pyqtSlot(int)
    def on_usesumrange_change(self, value):
        """Event: change if sumrange is used."""
        if self.UI_setting:
            return
        if value:
            if self.experiment_back.sumrange:
                var, range_ = self.experiment_back.sumrange
            else:
                var, range_ = "j", symbolic.Range((1, 1, 1))
            if (self.experiment.range and self.experiment.range[0] == var):
                var = "j" if self.experiment.range[0] == "i" else "i"
                self.experiment.sumrange = [var, symbolic.Range((1, 1, 1))]
        else:
            self.experiment_back.sumrange = self.experiment.sumrange
            # TODO: remove elsewhere
            self.experiment.sumrange = None
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
        if value:
            # TODO: change elsewhere
            self.experiment.sumrange[0] = value
        else:
            # TODO: invalid
            pass

    @pyqtSlot(str)
    def on_sumrangevals_change(self, value):
        """Event: change sumrange."""
        if self.UI_setting:
            return
        self.experiment.sumrange[1] = symbolic.Range(str(value))

    @pyqtSlot(int)
    def on_calls_parallel_change(self, value):
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
        # TODO

    def on_calls_focusout(self, event):
        """Event: unfocus calls."""
        # TODO


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
