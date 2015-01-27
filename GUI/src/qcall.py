#!/usr/bin/env python
from __future__ import division, print_function

import signature
from qdataarg import QDataArg

from PyQt4 import QtCore, QtGui


class QCall(QtGui.QFrame):
    def __init__(self, viewer, callid):
        QtGui.QGroupBox.__init__(self)
        self.viewer = viewer
        self.callid = callid
        self.sig = None

        self.UI_init()
        self.movers_setvisibility()

    def UI_init(self):
        # frame
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        routines = list(self.viewer.sampler["kernels"])

        # layout
        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        # buttons
        buttonsL = QtGui.QHBoxLayout()
        layout.addLayout(buttonsL, 0, 0)

        # buttons > remove
        self.Qt_removeS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_removeS)
        remove = QtGui.QToolButton()
        self.Qt_removeS.addWidget(remove)
        icon = self.style().standardIcon(QtGui.QStyle.SP_DialogDiscardButton)
        remove.setIcon(icon)
        remove.clicked.connect(self.remove_click)
        self.Qt_removeS.addWidget(QtGui.QWidget())

        # buttons > down
        self.Qt_movedownS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_movedownS)
        movedown = QtGui.QToolButton()
        movedown.setArrowType(QtCore.Qt.DownArrow)
        self.Qt_movedownS.addWidget(movedown)
        movedown.clicked.connect(self.movedown_click)
        self.Qt_movedownS.addWidget(QtGui.QWidget())

        # buttons > up
        self.Qt_moveupS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_moveupS)
        moveup = QtGui.QToolButton()
        moveup.setArrowType(QtCore.Qt.UpArrow)
        self.Qt_moveupS.addWidget(moveup)
        moveup.clicked.connect(self.moveup_click)
        self.Qt_moveupS.addWidget(QtGui.QWidget())

        # buttons
        buttonsL.addStretch(1)

        # routine
        routine = QtGui.QLineEdit()
        layout.addWidget(routine, 1, 0)
        routine.callid = self.callid
        routine.argid = 0
        routine.setProperty("invalid", True)
        routine.textChanged.connect(self.arg_change)
        completer = QtGui.QCompleter(routines, routine)
        routine.setCompleter(completer)

        # spaces
        layout.setColumnStretch(100, 1)

        # attributes
        self.Qt_args = [routine]
        self.Qt_arglabels = [None]
        self.sig = None

    def movers_setvisibility(self):
        ncalls = len(self.viewer.calls)
        if ncalls > 1:
            self.Qt_removeS.setCurrentIndex(0)
            if self.callid > 0:
                self.Qt_moveupS.setCurrentIndex(0)
            else:
                self.Qt_moveupS.setCurrentIndex(1)
            if self.callid < ncalls - 1:
                self.Qt_movedownS.setCurrentIndex(0)
            else:
                self.Qt_movedownS.setCurrentIndex(1)
        else:
            self.Qt_removeS.setCurrentIndex(1)
            self.Qt_moveupS.setCurrentIndex(1)
            self.Qt_movedownS.setCurrentIndex(1)

    def args_init(self):
        call = self.viewer.calls[self.callid]
        self.Qt_args[0].setProperty("invalid", False)
        if isinstance(call, signature.Call):
            self.sig = call.sig
        else:
            minsig = self.viewer.sampler["kernels"][call[0]]
            self.sig = None
            if not self.viewer.nosigwarning_shown:
                self.viewer.UI_alert("No signature found for %r!\n" % call[0] +
                                     "Hover arguments for input syntax.")
                self.viewer.nosigwarning_shown = True
        for argid in range(len(call))[1:]:
            tooltip = None
            if self.sig:
                argname = self.sig[argid].name
            else:
                argname = minsig[argid].replace("*", " *")
                if "char" in argname:
                    tooltip = "Any string"
                elif argname in ("int *", "float *", "double *"):
                    tooltip = ("Scalar:\tvalue\t\te.g. 1, -0.5\n"
                               "Array:\t[#elements]"
                               "\te.g. [10000] for a 100x100 matrix")
            Qarglabel = QtGui.QLabel(argname)
            if tooltip:
                Qarglabel.setToolTip(tooltip)
            self.layout().addWidget(Qarglabel, 0, argid)
            self.Qt_arglabels.append(Qarglabel)
            Qarglabel.setAlignment(QtCore.Qt.AlignCenter)
            if self.sig:
                arg = self.sig[argid]
                if isinstance(arg, signature.Flag):
                    Qarg = QtGui.QComboBox()
                    Qarg.addItems(arg.flags)
                    Qarg.currentIndexChanged.connect(self.arg_change)
                elif isinstance(arg, (signature.Dim, signature.Scalar,
                                      signature.Ld, signature.Inc,
                                      signature.Info)):
                    Qarg = QtGui.QLineEdit()
                    Qarg.textChanged.connect(self.arg_change)
                elif isinstance(arg, signature.Data):
                    Qarg = QDataArg(self)
            else:
                Qarg = QtGui.QLineEdit()
                Qarg.textChanged.connect(self.arg_change)
                if tooltip:
                    Qarg.setToolTip(tooltip)
            Qarg.argid = argid
            Qarg.setProperty("invalid", True)
            self.layout().addWidget(Qarg, 1, argid)
            self.Qt_args.append(Qarg)
        if self.sig:
            self.showargs_apply()
            self.usevary_apply()

    def args_clear(self):
        self.Qt_args[0].setProperty("invalid", True)
        for Qarg in self.Qt_args[1:]:
            Qarg.deleteLater()
        self.Qt_args = self.Qt_args[:1]
        for Qarglabel in self.Qt_arglabels[1:]:
            Qarglabel.deleteLater()
        self.Qt_arglabels = self.Qt_arglabels[:1]
        self.sig = None

    def showargs_apply(self):
        if not self.sig:
            return
        for argid, arg in enumerate(self.sig):
            for name, classes in (
                ("flags", signature.Flag),
                ("scalars", signature.Scalar),
                ("lds", (signature.Ld, signature.Inc)),
                ("infos", signature.Info)
            ):
                if isinstance(arg, classes):
                    showing = self.viewer.showargs[name]
                    self.Qt_arglabels[argid].setVisible(showing)
                    self.Qt_args[argid].setVisible(showing)

    def usevary_apply(self):
        if not self.sig:
            return
        for Qarg in self.Qt_args:
            if isinstance(Qarg, QDataArg):
                Qarg.usevary_apply()

    def args_set(self, fromargid=None):
        call = self.viewer.calls[self.callid]
        # set widgets
        if call[0] not in self.viewer.sampler["kernels"]:
            self.args_clear()
            return
        if isinstance(call, signature.Call):
            if call.sig != self.sig:
                self.args_clear()
                self.args_init()
        else:
            if len(self.Qt_args) != len(call):
                self.args_clear()
                self.args_init()
        # set values
        for argid, val in enumerate(call):
            Qarg = self.Qt_args[argid]
            Qarg.setProperty("invalid", val is None)
            Qarg.style().unpolish(Qarg)
            Qarg.style().polish(Qarg)
            Qarg.update()
            if Qarg.argid == fromargid:
                continue
            val = "" if val is None else str(val)
            if isinstance(Qarg, QtGui.QLineEdit):
                Qarg.setText(val)
            elif isinstance(Qarg, QtGui.QComboBox):
                Qarg.setCurrentIndex(Qarg.findText(val))
            elif isinstance(Qarg, QDataArg):
                Qarg.set()

    def data_viz(self):
        if not self.sig:
            return
        for argid in self.viewer.calls[self.callid].sig.dataargs():
            self.Qt_args[argid].viz()

    # event handlers
    def remove_click(self):
        self.viewer.UI_call_remove(self.callid)

    def moveup_click(self):
        self.viewer.UI_call_moveup(self.callid)

    def movedown_click(self):
        self.viewer.UI_call_movedown(self.callid)

    def arg_change(self):
        sender = self.viewer.app.sender()
        if isinstance(sender, QtGui.QLineEdit):
            # adjust widt no matter where the change came from
            val = str(sender.text())
            if sender.argid != 0:
                width = sender.fontMetrics().width(val)
                width += sender.minimumSizeHint().width()
                height = sender.sizeHint().height()
                sender.setFixedSize(max(height, width), height)
        if self.viewer.Qt_setting:
            return
        if isinstance(sender, QtGui.QComboBox):
            val = str(sender.currentText())
        if not val:
            val = None
        self.viewer.UI_arg_change(self.callid, sender.argid, val)
