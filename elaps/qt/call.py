#!/usr/bin/env python
"""Representation of calls in ELAPS:PlayMat."""
from __future__ import division, print_function

import signature
from dataarg import QDataArg

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot


class QCall(QtGui.QListWidgetItem):

    """Representation of a call in ELAPS:PlayMat."""

    def __init__(self, playmat, callid):
        """Initialize the call representation."""
        QtGui.QListWidgetItem.__init__(self)
        self.playmat = playmat
        self.sig = None

        self.UI_init()

    @property
    def callid(self):
        """Get the callid."""
        return self.playmat.UI_calls.row(self)

    @property
    def call(self):
        """Get the associalted Call (or BasicCall)."""
        return self.playmat.experiment.calls[self.callid]

    def UI_init(self):
        """Initialize the GUI elements."""
        routines = list(self.playmat.experiment.sampler["kernels"])

        # layout
        self.widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        self.widget.setLayout(layout)

        # routine label
        routinelabel = QtGui.QLabel()
        layout.addWidget(routinelabel, 0, 0)

        # routine
        routine = QtGui.QLineEdit(textChanged=self.on_arg_change)
        layout.addWidget(routine, 1, 0)
        routine.argid = 0
        completer = QtGui.QCompleter(routines, routine)
        routine.setCompleter(completer)

        # spaces
        layout.setColumnStretch(100, 1)

        # TODO: context menu

        # attributes
        self.UI_args = [routine]
        self.UI_arglabels = [routinelabel]
        self.sig = None

    def update_size(self):
        """Update the size of the call item from its widget."""
        def update():
            """Update the size (asynchronous callback)."""
            try:
                self.setSizeHint(self.widget.sizeHint())
            except:
                pass
        QtCore.QTimer.singleShot(0, update)

    def setall(self):
        """Set all UI elements."""
        self.playmat.UI_setting += 1
        self.fixcallid = self.callid
        if isinstance(self.call, signature.BasicCall):
            if self.sig != self.call.sig:
                self.args_clear()
                self.args_init()
                self.sig = self.call.sig
        else:
            if self.sig:
                self.args_clear()
                self.sig = None
        hideargs = tuple(self.playmat.hideargs) + (type(None),)
        for argid, value in enumerate(self.call):
            # set value
            value = value or ""
            UI_arg = self.UI_args[argid]
            UI_arglabel = self.UI_arglabels[argid]
            if not UI_arg.hasFocus():
                if isinstance(UI_arg, QtGui.QLineEdit):
                    UI_arg.setText(str(value))
                elif isinstance(UI_arg, QtGui.QComboBox):
                    UI_arg.setCurrentIndex(UI_arg.findText(str(value)))

            # set validity
            valid = self.playmat.experiment.check_arg_valid(self.callid, argid)
            UI_arg.setProperty("invalid", not valid)
            UI_arg.style().unpolish(UI_arg)
            UI_arg.style().polish(UI_arg)
            UI_arg.update()

            # apply hideargs
            if isinstance(self.call, signature.Call):
                show = not isinstance(self.sig[argid], hideargs)
                UI_arg.setVisible(show)
                UI_arglabel.setVisible(show)

        self.viz()
        self.update_size()
        self.playmat.UI_setting -= 1

    def args_init(self):
        """Initialize the arguments."""
        Qroutine = self.UI_args[0]
        assert(isinstance(self.call, signature.BasicCall))
        sig = self.call.sig
        doc = self.playmat.docs_get(self.call[0])
        if doc:
            Qroutine.setToolTip(doc[0][1])
        for argid, arg in enumerate(sig):
            if argid == 0:
                continue
            tooltip = ""
            if isinstance(sig, signature.Signature):
                argname = sig[argid].name
                if doc and argid < len(doc):
                    tooltip = doc[argid][1]
            else:
                argname = sig[argid].replace("*", " *")
                if doc and argid < len(doc):
                    argname += doc[argid][0]
                    tooltip = doc[argid][1]
                if argname in ("int *", "float *", "double *"):
                    if doc:
                        tooltip += "\n\n*Format*:\n"
                    tooltip += ("Scalar:\tvalue\t\te.g. 1, -0.5\n"
                                "Array:\t[#elements]"
                                "\te.g. [10000] for a 100x100 matrix")
            # arglabel
            UI_arglabel = QtGui.QLabel(
                argname, toolTip=tooltip, alignment=QtCore.Qt.AlignCenter
            )
            self.UI_arglabels.append(UI_arglabel)
            self.widget.layout().addWidget(UI_arglabel, 0, argid)
            # arg
            if isinstance(sig, signature.Signature):
                arg = sig[argid]
                if isinstance(arg, signature.Flag):
                    UI_arg = QtGui.QComboBox()
                    UI_arg.addItems(arg.flags)
                    UI_arg.currentIndexChanged[str].connect(self.on_arg_change)
                elif isinstance(arg, signature.Data):
                    UI_arg = QDataArg(self, textChanged=self.on_arg_change)
                else:
                    UI_arg = QtGui.QLineEdit(textChanged=self.on_arg_change)
            else:
                UI_arg = QtGui.QLineEdit("", textChanged=self.on_arg_change)
            UI_arg.pyqtConfigure(
                contextMenuPolicy=QtCore.Qt.CustomContextMenu,
                toolTip=tooltip,
                customContextMenuRequested=self.on_arg_rightclick
            )
            UI_arg.argid = argid
            self.UI_args.append(UI_arg)
            self.widget.layout().addWidget(UI_arg, 1, argid,
                                           QtCore.Qt.AlignCenter)

    def args_clear(self):
        """Clear the arguments."""
        for UI_arg in self.UI_args[1:]:
            UI_arg.deleteLater()
        self.UI_args = [self.UI_args[0]]
        for UI_arglabel in self.UI_arglabels[1:]:
            UI_arglabel.deleteLater()
        self.UI_arglabels = [self.UI_arglabels[0]]
        self.UI_args[0].setToolTip("")

    def viz(self):
        """Visualize all operands."""
        if not isinstance(self.call, signature.Call):
            return
        for argid in self.call.sig.dataargs():
            self.UI_args[argid].viz()
        self.update_size()

    # event handlers
    @pyqtSlot(str)
    def on_arg_change(self, value):
        """Event: Changed an argument."""
        sender = self.playmat.Qapp.sender()
        value = str(value)
        argid = sender.argid
        if isinstance(sender, QtGui.QLineEdit) and not isinstance(sender,
                                                                  QDataArg):
            # adjust widt no matter where the change came from
            width = sender.fontMetrics().width(value)
            width += sender.minimumSizeHint().width()
            width = min(width, sender.sizeHint().width())
            height = sender.sizeHint().height()
            if argid == 0:
                sender.setMinimumSize(max(height, width), height)
            else:
                sender.setFixedSize(max(height, width), height)
        if self.playmat.UI_setting:
            return
        self.playmat.on_arg_set(self.callid, argid, value)

    @pyqtSlot(QtCore.QPoint)
    def on_arg_rightclick(self, pos):
        """Event: right click on arg."""
        if self.playmat.UI_setting:
            return
        sender = self.playmat.Qapp.sender()
        globalpos = sender.mapToGlobal(pos)
        menu = sender.createStandardContextMenu()
        if isinstance(self.call, signature.Call):
            actions = menu.actions()
            argid = sender.argid
            if isinstance(self.call.sig[argid], signature.Ld):
                inferld = QtGui.QAction("Infer leading dimension", sender,
                                        triggered=self.on_inferld)
                inferld.argid = argid
                menu.insertAction(actions[0], inferld)
            elif isinstance(self.call.sig[argid], signature.Lwork):
                inferlwork = QtGui.QAction("Infer workspace size", sender,
                                           triggered=self.on_inferlwork)
                inferlwork.argid = argid
                menu.insertAction(actions[0], inferlwork)
            if isinstance(self.call.sig[argid], signature.Data):
                varyM = self.playmat.UI_varyM(self.call[argid])
                if isinstance(varyM, QtGui.QMenu):
                    menu.insertMenu(actions[0], varyM)
                elif isinstance(varyM, QtGui.QAction):
                    menu.insertAction(actions[0], varyM)
            if len(menu.actions()) > len(actions):
                menu.insertSeparator(actions[0])
        menu.exec_(globalpos)

    @pyqtSlot()
    def on_inferld(self):
        """Event: infer ld."""
        if self.playmat.UI_setting:
            return
        argid = self.playmat.Qapp.sender().argid
        self.UI_args[argid].clearFocus()
        self.playmat.on_infer_ld(self.callid, argid)

    @pyqtSlot()
    def on_inferlwork(self):
        """Event: infer ld."""
        if self.playmat.UI_setting:
            return
        argid = self.playmat.Qapp.sender().argid
        self.UI_args[argid].clearFocus()
        self.playmat.on_infer_lwork(self.callid, argid)
