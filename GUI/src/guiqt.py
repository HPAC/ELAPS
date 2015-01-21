#!/usr/bin/env python
from __future__ import division, print_function

from gui import GUI
from qcall import QCall

import os
import sys

from PyQt4 import QtCore, QtGui


class GUI_Qt(GUI, QtGui.QApplication):
    def __init__(self, loadstate=True):
        QtGui.QApplication.__init__(self, sys.argv)
        self.setting = False
        self.nosigwarning_shown = False
        GUI.__init__(self, loadstate)

    def UI_init(self):
        # window
        self.Qt_window = QtGui.QWidget()
        self.Qt_window.setWindowTitle("Sampler")
        windowL = QtGui.QVBoxLayout()
        self.Qt_window.setLayout(windowL)

        # window > top
        topL = QtGui.QHBoxLayout()
        windowL.addLayout(topL)

        # window > top > setup
        setupL = QtGui.QFormLayout()
        topL.addLayout(setupL)

        # window > top > setup > sampler
        self.Qt_sampler = QtGui.QComboBox()
        setupL.addRow("&Sampler:", self.Qt_sampler)
        self.Qt_sampler.addItems(sorted(self.samplers.keys()))
        self.Qt_sampler.currentIndexChanged.connect(self.Qt_sampler_change)

        # window > top > setup > nt
        self.Qt_nt = QtGui.QComboBox()
        setupL.addRow("#&threads:", self.Qt_nt)
        self.Qt_nt.currentIndexChanged.connect(self.Qt_nt_change)

        # window > top > setup > nrep
        self.Qt_nrep = QtGui.QLineEdit()
        setupL.addRow("&repetitions:", self.Qt_nrep)
        self.Qt_nrep.textChanged.connect(self.Qt_nrep_change)
        validator = QtGui.QIntValidator()
        self.Qt_nrep.setValidator(validator)
        validator.setBottom(0)

        # window > top > info
        info = QtGui.QGroupBox()
        topL.addWidget(info)
        infoL = QtGui.QVBoxLayout()
        info.setLayout(infoL)
        self.Qt_info = QtGui.QLabel()
        infoL.addWidget(self.Qt_info)
        self.Qt_info.setWordWrap(True)
        infoL.addStretch(1)

        # window > top > options
        optionsL = QtGui.QVBoxLayout()
        topL.addLayout(optionsL)

        # window > top > options > features
        features = QtGui.QGroupBox("features")
        optionsL.addWidget(features)
        featuresL = QtGui.QVBoxLayout()
        features.setLayout(featuresL)

        # window > top > options > features > usepapi
        self.Qt_usepapi = QtGui.QCheckBox("use PAPI")
        featuresL.addWidget(self.Qt_usepapi)
        self.Qt_usepapi.stateChanged.connect(self.Qt_usepapi_change)

        # window > top > options > features> usevary
        self.Qt_usevary = QtGui.QCheckBox("vary matrices across reps")
        featuresL.addWidget(self.Qt_usevary)
        self.Qt_usevary.stateChanged.connect(self.Qt_usevary_change)

        # window > top > options > features
        showargs = QtGui.QGroupBox("show arguments:")
        optionsL.addWidget(showargs)
        showargsL = QtGui.QVBoxLayout()
        showargs.setLayout(showargsL)

        self.Qt_showargs = {}
        # window > top > options > showargs >
        for name, desc in (
            ("flags", "flags"),
            ("scalars", "scalars"),
            ("lds", "leading dimensions"),
            ("infos", "info")
        ):
            checkbox = QtGui.QCheckBox(desc)
            showargsL.addWidget(checkbox)
            checkbox.argtype = name
            checkbox.stateChanged.connect(self.Qt_showargs_change)
            self.Qt_showargs[name] = checkbox

        # window > top > advanced
        optionsL.addStretch(1)

        # window > top > counters
        self.Qt_counters = QtGui.QGroupBox("PAPI counters")
        topL.addWidget(self.Qt_counters)
        countersL = QtGui.QVBoxLayout()
        self.Qt_counters.setLayout(countersL)

        # window > top
        topL.addStretch(1)

        # window > range
        rangeL = QtGui.QHBoxLayout()
        windowL.addLayout(rangeL)

        # window > range > userange
        self.Qt_userange = QtGui.QCheckBox("range")
        self.Qt_userange.stateChanged.connect(self.Qt_userange_change)
        rangeL.addWidget(self.Qt_userange)

        # window > range > rangevar
        self.Qt_rangevar = QtGui.QLineEdit()
        rangeL.addWidget(self.Qt_rangevar)
        self.Qt_rangevar.textChanged.connect(self.Qt_rangevar_change)
        self.Qt_rangevar.setFixedWidth(30)
        regexp = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(regexp, self)
        self.Qt_rangevar.setValidator(validator)
        self.Qt_rangevar.hide()

        # window > range > "="
        self.Qt_rangelabel = QtGui.QLabel("=")
        rangeL.addWidget(self.Qt_rangelabel)

        # window > range > range
        self.Qt_range = QtGui.QLineEdit()
        rangeL.addWidget(self.Qt_range)
        self.Qt_range.textChanged.connect(self.Qt_range_change)
        regexp = QtCore.QRegExp("(?:-?\d+)?:(?:(?:-?\d+)?:)?(-?\d+)?")
        validator = QtGui.QRegExpValidator(regexp, self)
        self.Qt_range.setValidator(validator)

        # window > range
        rangeL.addStretch(1)

        # window > calls
        callsSA = QtGui.QScrollArea()
        windowL.addWidget(callsSA)
        callsSA.setMinimumHeight(200)
        callsSA.setMinimumWidth(900)
        self.Qt_calls = QtGui.QWidget()
        callsSA.setWidget(self.Qt_calls)
        callsL = QtGui.QVBoxLayout()
        self.Qt_calls.setLayout(callsL)
        callsL.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        windowL.setStretch(2, 1)
        self.Qt_Qcalls = []

        # window > calls > add
        add = QtGui.QPushButton("+")
        callsL.addWidget(add)
        add.clicked.connect(self.Qt_call_add)

        # window > calls
        callsL.addStretch(1)

        # window > bottom
        bottomL = QtGui.QHBoxLayout()
        windowL.addLayout(bottomL)
        bottomL.addStretch(1)

        # window > bottom > submit
        self.Qt_submit = QtGui.QPushButton("submit")
        bottomL.addWidget(self.Qt_submit)
        self.Qt_submit.clicked.connect(self.Qt_submit_click)

        # window
        self.Qt_window.show()

        # style
        self.setStyleSheet("""
            QLineEdit[invalid="true"],
            *[invalid="true"] QLineEdit {
                background: #FFDDDD;
            }
        """)

        # pens (for dataargs)
        self.Qt_pens = {
            None: QtGui.QColor(0, 0, 255, 0),
            "maxfront": QtGui.QColor(127, 127, 255, 127),
            "maxback": QtGui.QPen(QtGui.QColor(127, 127, 255, 127), 0,
                                  style=QtCore.Qt.DashLine),
            "minfront": QtGui.QColor(127, 127, 255),
            "minback": QtGui.QPen(QtGui.QColor(127, 127, 255), 0,
                                  style=QtCore.Qt.DashLine),
        }
        self.Qt_brushes = {
            "max": QtGui.QColor(255, 255, 255, 127),
            "min": QtGui.QColor(255, 255, 255, 255),
        }

        self.Qt_jobprogress_init()

    def Qt_jobprogress_init(self):

        # window
        self.Qt_jobprogress = QtGui.QWidget()
        self.Qt_jobprogress.setWindowTitle("Job progress")
        layout = QtGui.QGridLayout()
        self.Qt_jobprogress.setLayout(layout)
        close = QtGui.QPushButton("hide")
        layout.addWidget(close, 100, 3)
        close.clicked.connect(self.Qt_jobprogress.hide)

        # timer
        self.Qt_jobprogress_items = []
        self.Qt_jobprogress_timer = QtCore.QTimer()
        self.Qt_jobprogress_timer.setInterval(1000)
        self.Qt_jobprogress_timer.timeout.connect(self.UI_jobprogress_update)

    def UI_start(self):
        sys.exit(self.exec_())

    # dialogs
    def UI_alert(self, *args, **kwargs):
        msg = " ".join(map(str, args))
        title = kwargs.get("title", "")
        self.UI_dialog("information", title, msg)

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
        self.setting = True
        self.Qt_sampler.setCurrentIndex(
            self.Qt_sampler.findText(self.samplername)
        )
        self.setting = False

    def UI_nt_setmax(self):
        self.setting = True
        self.Qt_nt.clear()
        self.Qt_nt.addItems(map(str, range(1, self.sampler["nt_max"] + 1)))
        self.setting = False

    def UI_nt_set(self):
        self.setting = True
        self.Qt_nt.setCurrentIndex(self.nt - 1)
        self.setting = False

    def UI_nrep_set(self):
        self.setting = True
        self.Qt_nrep.setText(str(self.nrep))
        self.setting = False

    def UI_info_set(self, text):
        self.Qt_info.setText(text)

    def UI_usepapi_setenabled(self):
        self.Qt_usepapi.setEnabled(self.sampler["papi_counters_max"] > 0)

    def UI_usepapi_set(self):
        self.setting = True
        self.Qt_usepapi.setChecked(self.usepapi)
        self.setting = False

    def UI_usevary_set(self):
        self.setting = True
        self.Qt_usevary.setChecked(self.usevary)
        self.setting = False

    def UI_showargs_set(self, name=None):
        if name is None:
            for name in self.Qt_showargs:
                self.UI_showargs_set(name)
            return
        self.setting = True
        self.Qt_showargs[name].setChecked(self.showargs[name])
        self.setting = False

    def UI_counters_setvisible(self):
        self.Qt_counters.setVisible(self.usepapi)

    def UI_counters_setoptions(self):
        # delete old
        Qcounters = self.Qt_counters.children()[1:]
        for Qcounter in Qcounters:
            Qcounter.deleteLater()
        # add new
        QcountersL = self.Qt_counters.layout()
        for _ in range(self.sampler["papi_counters_max"]):
            Qcounter = QtGui.QComboBox()
            QcountersL.addWidget(Qcounter)
            Qcounter.addItems([""] + self.sampler["papi_counters_avail"])
            Qcounter.currentIndexChanged.connect(self.Qt_counter_change)

    def UI_counters_set(self):
        self.setting = True
        Qcounters = self.Qt_counters.children()[1:]
        for Qcounter, countername in zip(Qcounters, self.counters):
            if not countername:
                countername = ""
            Qcounter.setCurrentIndex(Qcounter.findText(countername))
        self.setting = False

    def UI_userange_set(self):
        self.setting = True
        self.Qt_userange.setChecked(self.userange)
        self.setting = False

    def UI_range_setvisible(self):
        self.Qt_rangevar.setVisible(self.userange)
        self.Qt_rangelabel.setVisible(self.userange)
        self.Qt_range.setVisible(self.userange)

    def UI_rangevar_set(self):
        self.setting = True
        self.Qt_rangevar.setText(self.rangevar)
        self.setting = False

    def UI_range_set(self):
        self.setting = True
        lower, upper, step = self.range
        if step:
            self.Qt_range.setText("%d:%d:%d" % (lower, step, upper - 1))
        elif lower and upper:
            self.Qt_range.setText("%d:%d" % (lower, upper - 1))
        elif lower:
            self.Qt_range.setText("%d:" % lower)
        elif upper:
            self.Qt_range.setText(":%d" % upper)
        else:
            self.Qt_range.setText("")
        self.setting = False

    def UI_calls_init(self):
        self.setting = True
        # delete old
        for Qcall in self.Qt_Qcalls:
            Qcall.deleteLater()
        self.Qt_Qcalls = []
        # add new
        QcallsL = self.Qt_calls.layout()
        for callid in range(len(self.calls)):
            Qcall = QCall(self, callid)
            QcallsL.insertWidget(callid, Qcall)
            self.Qt_Qcalls.append(Qcall)
            Qcall.args_set()
        QcallsL.invalidate()
        QcallsL.activate()
        self.setting = False

    def UI_call_set(self, callid, fromargid=None):
        self.setting = True
        self.Qt_Qcalls[callid].args_set(fromargid)
        self.setting = False

    def UI_calls_set(self, fromcallid=None, fromargid=None):
        self.setting = True
        for callid, Qcall in enumerate(self.Qt_Qcalls):
            Qcall.args_set(fromargid if fromcallid == callid else None)
        self.setting = False

    def UI_data_viz(self):
        self.setting = True
        for Qcall in self.Qt_Qcalls:
            Qcall.data_viz()
        self.setting = False

    def UI_showargs_apply(self):
        for Qcall in self.Qt_Qcalls:
            Qcall.showargs_apply()

    def UI_usevary_apply(self):
        for Qcall in self.Qt_Qcalls:
            Qcall.usevary_apply()

    def UI_submit_setenabled(self):
        if self.calls_checksanity():
            self.Qt_submit.setEnabled(True)
        else:
            self.Qt_submit.setEnabled(False)

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
        self.Qt_jobprogress.hide()
        self.Qt_jobprogress.show()
        self.UI_jobprogress_update()
        self.Qt_jobprogress_timer.start()

    # event handlers
    def Qt_sampler_change(self):
        if self.setting:
            return
        self.UI_sampler_change(str(self.Qt_sampler.currentText()))

    def Qt_nt_change(self):
        if self.setting:
            return
        self.UI_nt_change(int(self.Qt_nt.currentText()))

    def Qt_nrep_change(self):
        if self.setting:
            return
        text = str(self.Qt_nrep.text())
        self.UI_nrep_change(int(text) if text else None)

    def Qt_usepapi_change(self):
        if self.setting:
            return
        self.UI_usepapi_change(self.Qt_usepapi.isChecked())

    def Qt_showargs_change(self):
        if self.setting:
            return
        sender = self.sender()
        self.UI_showargs_change(sender.argtype, sender.isChecked())

    def Qt_usevary_change(self):
        if self.setting:
            return
        self.UI_usevary_change(self.Qt_usevary.isChecked())
        self.UI_data_viz()

    def Qt_counter_change(self):
        if self.setting:
            return
        counternames = []
        Qcounters = self.Qt_counters.children()[1:]
        for Qcounter in Qcounters:
            countername = str(Qcounter.currentText())
            counternames.append(countername if countername else None)
        self.UI_counters_change(counternames)

    def Qt_userange_change(self):
        if self.setting:
            return
        self.UI_userange_change(self.Qt_userange.isChecked())

    def Qt_rangevar_change(self):
        if self.setting:
            return
        self.UI_rangevar_change(str(self.Qt_rangevar.text()))

    def Qt_range_change(self):
        if self.setting:
            return
        parts = str(self.Qt_range.text()).split(":")
        lower = int(parts[0]) if len(parts) >= 1 and parts[0] else None
        step = int(parts[1]) if len(parts) == 3 and parts[1] else 1
        upper = int(parts[-1]) + 1 if len(parts) >= 2 and parts[-1] else None
        self.UI_range_change((lower, upper, step))

    def Qt_call_add(self):
        self.UI_call_add()

    def Qt_submit_click(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            self.Qt_window,
            "Generate report as",
            self.reportpath,
            "*.smpl"
        )
        filename = str(filename)
        if filename:
            self.UI_submit(filename)

    def Qt_jobprogress_click(self):
        sender = self.sender()
        jobid = sender.jobid
        job = self.jobprogress[jobid]
        if job["progress"] <= job["progressend"]:
            self.UI_jobkill(jobid)
        else:
            self.UI_jobview(jobid)


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    loadstate = "-newstate" not in sys.argv[1:]
    GUI_Qt(loadstate)


if __name__ == "__main__":
    main()
