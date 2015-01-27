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
        self.setting = False
        GUI.__init__(self, loadstate)

    def UI_init(self):
        # window
        self.Qt_window = QtGui.QMainWindow()
        self.Qt_window.setWindowTitle("Sampler")

        # MENU

        menu = self.Qt_window.menuBar()

        # menu > options
        options = menu.addMenu("Options")

        # menu > options > usentrange
        self.Qt_usentrange = QtGui.QAction("#threads range", self.Qt_window)
        options.addAction(self.Qt_usentrange)
        self.Qt_usentrange.setCheckable(True)
        self.Qt_usentrange.toggled.connect(self.Qt_usentrange_toggle)

        # menu > options > userange
        self.Qt_userange = QtGui.QAction("for each range", self.Qt_window)
        options.addAction(self.Qt_userange)
        self.Qt_userange.setCheckable(True)
        self.Qt_userange.toggled.connect(self.Qt_userange_toggle)

        # menu > options > usesumrange
        self.Qt_usesumrange = QtGui.QAction("sum over sumrange", self.Qt_window)
        options.addAction(self.Qt_usesumrange)
        self.Qt_usesumrange.setCheckable(True)
        self.Qt_usesumrange.toggled.connect(self.Qt_usesumrange_toggle)

        # menu > options > usepapi
        self.Qt_usepapi = QtGui.QAction("use papi", self.Qt_window)
        options.addAction(self.Qt_usepapi)
        self.Qt_usepapi.setCheckable(True)
        self.Qt_usepapi.toggled.connect(self.Qt_usepapi_toggle)

        # menu > options > usevary
        self.Qt_usevary = QtGui.QAction("vary matrices", self.Qt_window)
        options.addAction(self.Qt_usevary)
        self.Qt_usevary.setCheckable(True)
        self.Qt_usevary.toggled.connect(self.Qt_usevary_toggle)

        # menu > view
        view = menu.addMenu("View")

        # menu > view > showargs
        self.Qt_showargs = {}
        for name, desc in (
            ("flags", "show flag arguments"),
            ("scalars", "show scalar arguments"),
            ("lds", "show leading dimensions"),
            ("infos", "show info arguments")
        ):
            showarg = QtGui.QAction(desc, self.Qt_window)
            view.addAction(showarg)
            showarg.setCheckable(True)
            showarg.toggled.connect(self.Qt_showarg_toggle)
            showarg.argtype = name
            self.Qt_showargs[name] = showarg

        # TOOLBARS

        # sampler
        samplerT = self.Qt_window.addToolBar("Sampler")

        # sampler > sampler
        self.Qt_sampler = QtGui.QComboBox()
        samplerT.addWidget(self.Qt_sampler)
        self.Qt_sampler.addItems(sorted(self.samplers.keys()))
        self.Qt_sampler.currentIndexChanged.connect(self.Qt_sampler_change)

        # sampler > about
        icon = self.app.style().standardIcon(QtGui.QStyle.SP_FileDialogInfoView)
        about = QtGui.QAction(icon, "about", self.Qt_window)
        about.triggered.connect(self.Qt_sampler_about)
        samplerT.addAction(about)

        # sampler > nt
        self.Qt_ntlabel = QtGui.QLabel("#threads:")
        samplerT.addWidget(self.Qt_ntlabel)
        self.Qt_nt = QtGui.QComboBox()
        samplerT.addWidget(self.Qt_nt)
        self.Qt_nt.currentIndexChanged.connect(self.Qt_nt_change)

        # sampler > submit
        icon = self.app.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)
        self.Qt_submit = QtGui.QAction(icon, "submit", self.Qt_window)
        samplerT.addAction(self.Qt_submit)
        self.Qt_submit.triggered.connect(self.Qt_submit_click)

        self.Qt_window.addToolBarBreak()

        # ranges
        rangesT = self.Qt_window.addToolBar("Ranges")
        rangesW = QtGui.QWidget()
        rangesT.addWidget(rangesW)
        rangesL = QtGui.QVBoxLayout()
        rangesW.setLayout(rangesL)
        margins = list(rangesL.getContentsMargins())
        margins[1] = margins[3] = 0
        rangesL.setContentsMargins(*margins)
        rangesL.setSpacing(0)

        # ranges > ntrange
        self.Qt_ntrangeW = QtGui.QWidget()
        rangesL.addWidget(self.Qt_ntrangeW)
        ntrangeL = QtGui.QHBoxLayout()
        self.Qt_ntrangeW.setLayout(ntrangeL)
        ntrangeL.setContentsMargins(0, 12, 12, 4)

        # ranges > ntrange > "for #threads nt ="
        ntrangeL.addWidget(QtGui.QLabel("for #threads nt ="))

        # ranges > ntrange > ntrange
        self.Qt_ntrange = QtGui.QLineEdit()
        ntrangeL.addWidget(self.Qt_ntrange)
        self.Qt_ntrange.textChanged.connect(self.Qt_ntrange_change)
        regexp = QtCore.QRegExp("(?:\d+)?:(?:(?:\d+)?:)?(\d+)?")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_ntrange.setValidator(validator)

        # ranges > ntrange
        ntrangeL.addStretch(1)

        # ranges > range
        self.Qt_rangeW = QtGui.QWidget()
        rangesL.addWidget(self.Qt_rangeW)
        rangeL = QtGui.QHBoxLayout()
        self.Qt_rangeW.setLayout(rangeL)
        rangeL.setContentsMargins(0, 12, 12, 4)

        # ranges > range > "for"
        rangeL.addWidget(QtGui.QLabel("for"))

        # ranges > range > rangevar
        self.Qt_rangevar = QtGui.QLineEdit()
        rangeL.addWidget(self.Qt_rangevar)
        self.Qt_rangevar.textChanged.connect(self.Qt_rangevar_change)
        self.Qt_rangevar.setFixedWidth(32)
        regexp = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_rangevar.setValidator(validator)

        # ranges > range > "="
        rangeL.addWidget(QtGui.QLabel("="))

        # ranges > range > range
        self.Qt_range = QtGui.QLineEdit()
        rangeL.addWidget(self.Qt_range)
        self.Qt_range.textChanged.connect(self.Qt_range_change)
        regexp = QtCore.QRegExp("(?:-?\d+)?:(?:(?:-?\d+)?:)?(-?\d+)?")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_range.setValidator(validator)

        # ranges > range
        rangeL.addStretch(1)

        # ranges > nrep
        nrepW = QtGui.QWidget()
        rangesL.addWidget(nrepW)
        nrepL = QtGui.QHBoxLayout()
        nrepW.setLayout(nrepL)
        nrepL.setContentsMargins(16, 0, 12, 4)

        # ranges > nrep > "repeat"
        nrepL.addWidget(QtGui.QLabel("repeat"))

        # ranges > nrep > nrep
        self.Qt_nrep = QtGui.QLineEdit()
        nrepL.addWidget(self.Qt_nrep)
        self.Qt_nrep.textChanged.connect(self.Qt_nrep_change)
        self.Qt_nrep.setFixedWidth(32)
        regexp = QtCore.QRegExp("[1-9][0-9]*")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_nrep.setValidator(validator)

        # ranges > nrep > "times"
        nrepL.addWidget(QtGui.QLabel("times"))

        # ranges > range
        nrepL.addStretch(1)

        # ranges > sumrange
        self.Qt_sumrangeW = QtGui.QWidget()
        rangesL.addWidget(self.Qt_sumrangeW)
        sumrangeL = QtGui.QHBoxLayout()
        self.Qt_sumrangeW.setLayout(sumrangeL)
        sumrangeL.setContentsMargins(32, 0, 12, 0)

        # ranges > sumrange > "for"
        sumrangeL.addWidget(QtGui.QLabel("sum over"))

        # ranges > sumrange > sumrangevar
        self.Qt_sumrangevar = QtGui.QLineEdit()
        sumrangeL.addWidget(self.Qt_sumrangevar)
        self.Qt_sumrangevar.textChanged.connect(self.Qt_sumrangevar_change)
        self.Qt_sumrangevar.setFixedWidth(32)
        regexp = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_sumrangevar.setValidator(validator)

        # ranges > sumrange > "="
        sumrangeL.addWidget(QtGui.QLabel("="))

        # ranges > sumrange > sumrange
        self.Qt_sumrange = QtGui.QLineEdit()
        sumrangeL.addWidget(self.Qt_sumrange)
        self.Qt_sumrange.textChanged.connect(self.Qt_sumrange_change)
        regexp = QtCore.QRegExp("(?:.*)?:(?:(?:.*)?:)?(.*)?")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.Qt_sumrange.setValidator(validator)

        # ranges > sumrange
        sumrangeL.addStretch(1)

        # counters
        self.Qt_counters = QtGui.QToolBar("PAPI counters")
        self.Qt_window.addToolBar(QtCore.Qt.RightToolBarArea, self.Qt_counters)
        self.Qt_counters.setOrientation(QtCore.Qt.Vertical)
        self.Qt_Qcounters = []

        # CALLS

        # window > calls
        callsSA = QtGui.QScrollArea()
        self.Qt_window.setCentralWidget(callsSA)
        callsSA.setMinimumHeight(240)
        self.Qt_calls = QtGui.QWidget()
        callsSA.setWidget(self.Qt_calls)
        callsL = QtGui.QVBoxLayout()
        self.Qt_calls.setLayout(callsL)
        callsL.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.Qt_Qcalls = []

        # window > calls > add
        add = QtGui.QPushButton("+")
        callsL.addWidget(add)
        add.clicked.connect(self.Qt_call_add)

        # window > calls
        callsL.addStretch(1)

        # window
        self.Qt_window.show()

        # STYLE

        # stylesheet
        self.app.setStyleSheet("""
            QLineEdit[invalid="true"],
            *[invalid="true"] QLineEdit {
                background: #FFDDDD;
            }
        """)

        # pens and brushes (for dataargs)
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

        self.Qt_viewer = None

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
        sys.exit(self.app.exec_())

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

    def UI_userange_setenabled(self):
        self.Qt_usentrange.setEnabled(not self.userange)
        self.Qt_userange.setEnabled(not self.usentrange)
        self.Qt_ntlabel.setVisible(not self.usentrange)
        self.Qt_nt.setVisible(not self.usentrange)

    def UI_usentrange_set(self):
        self.setting = True
        self.Qt_usentrange.setChecked(self.usentrange)
        self.setting = False

    def UI_usentrange_apply(self):
        self.Qt_ntrangeW.setVisible(self.usentrange)

    def UI_userange_set(self):
        self.setting = True
        self.Qt_userange.setChecked(self.userange)
        self.setting = False

    def UI_userange_apply(self):
        self.Qt_rangeW.setVisible(self.userange)

    def UI_usesumrange_set(self):
        self.setting = True
        self.Qt_usesumrange.setChecked(self.usesumrange)
        self.setting = False

    def UI_usesumrange_apply(self):
        self.Qt_sumrangeW.setVisible(self.usesumrange)

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
        for Qcounter in self.Qt_Qcounters:
            Qcounter.deleteLater()

        # add new
        for _ in range(self.sampler["papi_counters_max"]):
            Qcounter = QtGui.QComboBox()
            self.Qt_counters.addWidget(Qcounter)
            Qcounter.addItem("", QtCore.QVariant(""))
            for i, name in enumerate(self.sampler["papi_counters_avail"]):
                event = papi.events[name]
                Qcounter.addItem(event["short"], QtCore.QVariant(name))
                Qcounter.setItemData(i, name + "\n" + event["long"],
                                     QtCore.Qt.ToolTipRole)
            Qcounter.currentIndexChanged.connect(self.Qt_counter_change)

    def UI_counters_set(self):
        self.setting = True
        Qcounters = self.Qt_counters.children()[1:]
        for Qcounter, countername in zip(Qcounters, self.counters):
            index = Qcounter.findData(QtCore.QVariant(countername))
            Qcounter.setCurrentIndex(index)
            tip = ""
            if countername:
                tip = countername + "\n" + papi.events[countername]["long"]
            Qcounter.setToolTip(tip)
        self.setting = False

    def UI_ntrange_set(self):
        self.setting = True
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
        self.setting = False

    def UI_rangevar_set(self):
        self.setting = True
        self.Qt_rangevar.setText(self.rangevar)
        self.setting = False

    def UI_range_set(self):
        self.setting = True
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
        self.setting = False

    def UI_nrep_set(self):
        self.setting = True
        text = str(self.nrep) if self.nrep else ""
        self.Qt_nrep.setText(text)
        self.setting = False

    def UI_sumrangevar_set(self):
        self.setting = True
        self.Qt_sumrangevar.setText(self.sumrangevar)
        self.setting = False

    def UI_sumrange_set(self):
        self.setting = True
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

    def UI_viewer_load(self, filename):
        if self.Qt_viewer is None:
            from viewerqtmpl import Viewer_Qt_MPL
            self.Qt_viewer = Viewer_Qt_MPL(self.app)
        self.Qt_viewer.UI_load_report(filename)
        self.Qt_viewer.Qt_window.show()

    # event handlers
    def Qt_sampler_change(self):
        if self.setting:
            return
        self.UI_sampler_change(str(self.Qt_sampler.currentText()))

    def Qt_sampler_about(self):
        self.UI_alert(self.get_infostr(), title=self.samplername)

    def Qt_nt_change(self):
        if self.setting:
            return
        self.UI_nt_change(int(self.Qt_nt.currentText()))

    def Qt_usentrange_toggle(self, checked):
        if self.setting:
            return
        self.UI_usentrange_change(checked)

    def Qt_userange_toggle(self, checked):
        if self.setting:
            return
        self.UI_userange_change(checked)

    def Qt_usesumrange_toggle(self, checked):
        if self.setting:
            return
        self.UI_usesumrange_change(checked)

    def Qt_usepapi_toggle(self, checked):
        if self.setting:
            return
        self.UI_usepapi_change(checked)

    def Qt_usevary_toggle(self, checked):
        if self.setting:
            return
        self.UI_usevary_change(checked)

    def Qt_showarg_toggle(self, checked):
        if self.setting:
            return
        argtype = self.app.sender().argtype
        self.UI_showargs_change(argtype, checked)

    def Qt_counter_change(self):
        if self.setting:
            return
        counternames = []
        Qcounters = self.Qt_counters.children()[1:]
        for Qcounter in Qcounters:
            countername = str(
                Qcounter.itemData(Qcounter.currentIndex()).toString()
            )
            counternames.append(countername if countername else None)
            tip = ""
            if countername:
                tip = countername + "\n" + papi.events[countername]["long"]
            Qcounter.setToolTip(tip)
        self.UI_counters_change(counternames)

    def Qt_ntrange_change(self):
        if self.setting:
            return
        parts = str(self.Qt_ntrange.text()).split(":")
        lower = int(parts[0]) if len(parts) >= 1 and parts[0] else None
        step = int(parts[1]) if len(parts) == 3 and parts[1] else 1
        upper = int(parts[-1]) if len(parts) >= 2 and parts[-1] else None
        self.UI_ntrange_change((lower, step, upper))

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
        upper = int(parts[-1]) if len(parts) >= 2 and parts[-1] else None
        self.UI_range_change((lower, step, upper))

    def Qt_nrep_change(self):
        if self.setting:
            return
        text = str(self.Qt_nrep.text())
        self.UI_nrep_change(int(text) if text else None)

    def Qt_sumrangevar_change(self):
        if self.setting:
            return
        self.UI_sumrangevar_change(str(self.Qt_sumrangevar.text()))

    def Qt_sumrange_change(self):
        if self.setting:
            return
        parts = str(self.Qt_sumrange.text()).split(":")
        lower = parts[0] if len(parts) >= 1 else None
        step = parts[1] if len(parts) == 3 else 1
        upper = parts[-1] if len(parts) >= 2 else None
        self.UI_sumrange_change((lower, step, upper))

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

    def Qt_call_add(self):
        self.UI_call_add()

    def Qt_jobprogress_click(self):
        sender = self.app.sender()
        jobid = sender.jobid
        job = self.jobprogress[jobid]
        if job["progress"] <= job["progressend"]:
            self.UI_jobkill(jobid)
        else:
            self.UI_jobview(jobid)


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    loadstate = "--reset" not in sys.argv[1:]
    GUI_Qt(loadstate=loadstate).start()


if __name__ == "__main__":
    main()
