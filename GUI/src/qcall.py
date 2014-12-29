#!/usr/bin/env python
from __future__ import division, print_function

import signature
from qdataarg import QDataArg

from PyQt4 import QtCore, QtGui


class QCall(QtGui.QFrame):
    def __init__(self, app, callid):
        QtGui.QFrame.__init__(self)
        self.app = app
        self.callid = callid
        self.sig = None

        self.UI_init()
        self.movers_setvisibility()

    def UI_init(self):
        sampler = self.app.samplers[self.app.state["sampler"]]
        routines = [r for r in self.app.signatures.keys()
                    if r in sampler["kernels"]]

        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        # buttons
        buttonsL = QtGui.QHBoxLayout()
        layout.addLayout(buttonsL, 0, 0)

        # buttons > remove
        self.removeS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.removeS)
        remove = QtGui.QToolButton()
        self.removeS.addWidget(remove)
        icon = self.style().standardIcon(QtGui.QStyle.SP_DialogDiscardButton)
        remove.setIcon(icon)
        remove.clicked.connect(self.remove_click)
        self.removeS.addWidget(QtGui.QWidget())

        # buttons > down
        self.movedownS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.movedownS)
        movedown = QtGui.QToolButton()
        movedown.setArrowType(QtCore.Qt.DownArrow)
        self.movedownS.addWidget(movedown)
        movedown.clicked.connect(self.movedown_click)
        self.movedownS.addWidget(QtGui.QWidget())

        # buttons > up
        self.moveupS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.moveupS)
        moveup = QtGui.QToolButton()
        moveup.setArrowType(QtCore.Qt.UpArrow)
        self.moveupS.addWidget(moveup)
        moveup.clicked.connect(self.moveup_click)
        self.moveupS.addWidget(QtGui.QWidget())

        # buttons
        buttonsL.addStretch(1)

        # routine
        routine = QtGui.QLineEdit()
        layout.addWidget(routine, 1, 0)
        routine.callid = self.callid
        routine.argid = 0
        routine.setProperty("valid", False)
        routine.textChanged.connect(self.arg_change)
        completer = QtGui.QCompleter(routines, routine)
        routine.setCompleter(completer)

        # spaces
        layout.setColumnStretch(100, 1)

        # attributes
        self.args = [routine]
        self.arglabels = [None]
        self.sig = None

    def movers_setvisibility(self):
        ncalls = len(self.app.state["calls"])
        if ncalls > 1:
            self.removeS.setCurrentIndex(0)
            if self.callid > 0:
                self.moveupS.setCurrentIndex(0)
            else:
                self.moveupS.setCurrentIndex(1)
            if self.callid < ncalls - 1:
                self.movedownS.setCurrentIndex(0)
            else:
                self.movedownS.setCurrentIndex(1)
        else:
            self.removeS.setCurrentIndex(1)
            self.moveupS.setCurrentIndex(1)
            self.movedownS.setCurrentIndex(1)

    def args_init(self):
        call = self.app.state["calls"][self.callid]
        assert isinstance(call, signature.Call)
        assert len(self.args) == 1
        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Name):
                continue  # routine name
            Qarglabel = QtGui.QLabel(arg.name)
            self.layout().addWidget(Qarglabel, 0, argid)
            self.arglabels.append(Qarglabel)
            Qarglabel.setAlignment(QtCore.Qt.AlignCenter)
            if isinstance(arg, signature.Flag):
                Qarg = QtGui.QComboBox()
                Qarg.addItems(arg.flags)
                Qarg.currentIndexChanged.connect(self.arg_change)
            elif isinstance(arg, (signature.Dim, signature.Scalar,
                                  signature.Ld, signature.Inc)):
                Qarg = QtGui.QLineEdit()
                Qarg.textChanged.connect(self.arg_change)
            elif isinstance(arg, signature.Data):
                Qarg = QDataArg(self)
            Qarg.argid = argid
            Qarg.setProperty("invalid", True)
            self.layout().addWidget(Qarg, 1, argid)
            self.args.append(Qarg)
        self.sig = call.sig
        self.useld_apply()

    def args_clear(self):
        for Qarg in self.args[1:]:
            Qarg.deleteLater()
        self.args = self.args[:1]
        for Qarglabel in self.arglabels[1:]:
            Qarglabel.deleteLater()
        self.arglabels = self.arglabels[:1]
        self.sig = None

    def useld_apply(self):
        if not self.sig:
            return
        useld = self.app.state["useld"]
        for argid, arg in enumerate(self.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                if useld:
                    self.arglabels[argid].show()
                    self.args[argid].show()
                else:
                    self.arglabels[argid].hide()
                    self.args[argid].hide()

    def args_set(self, fromarg=None):
        call = self.app.state["calls"][self.callid]
        # set widgets
        if not isinstance(call, signature.Call):
            self.args_clear()
            return
        if call.sig != self.sig:
            self.args_clear()
            self.args_init()
        # set values
        for Qarg, arg, val in zip(self.args, call.sig, call):
            Qarg.setProperty("invalid", val is None)
            Qarg.style().unpolish(Qarg)
            Qarg.style().polish(Qarg)
            Qarg.update()
            if Qarg.argid == fromarg:
                continue
            val = "" if val is None else str(val)
            if isinstance(arg, (signature.Name, signature.Dim,
                                signature.Scalar, signature.Ld,
                                signature.Inc)):
                Qarg.setText(val)
                size = Qarg.minimumSizeHint()
                width = Qarg.fontMetrics().width(val[2:])
                Qarg.setFixedSize(size.width() + width, size.height())
            elif isinstance(arg, signature.Flag):
                Qarg.setCurrentIndex(Qarg.findText(val))
            elif isinstance(arg, signature.Data):
                Qarg.set()

    # event handlers
    def remove_click(self):
        self.app.UI_call_remove(self.callid)

    def moveup_click(self):
        self.app.UI_call_moveup(self.callid)

    def movedown_click(self):
        self.app.UI_call_movedown(self.callid)

    def arg_change(self):
        if self.app.setting:
            return
        sender = self.app.sender()
        argid = sender.argid
        if isinstance(sender, QtGui.QLineEdit):
            val = str(sender.text())
            size = sender.minimumSizeHint()
            width = sender.fontMetrics().width(val[2:])
            sender.setFixedSize(size.width() + width, size.height())
        elif isinstance(sender, QtGui.QComboBox):
            val = str(sender.currentText())
        if not val:
            val = None
        self.app.UI_arg_change(self.callid, argid, val)
