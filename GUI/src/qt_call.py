#!/usr/bin/env python
"""Representation of calls in the Qt Mat."""
from __future__ import division, print_function

import signature
from qt_dataarg import QDataArg

from PyQt4 import QtCore, QtGui


class QCall(QtGui.QListWidgetItem):

    """Representation of a call in the Qt GUI."""

    def __init__(self, gui, callid):
        """Initialize the call representation."""
        QtGui.QListWidgetItem.__init__(self)
        self.Qt_gui = gui
        self.callid = callid
        self.sig = None

        self.UI_init()

    def UI_init(self):
        """Initialize the GUI elements."""
        routines = list(self.Qt_gui.sampler["kernels"])

        # layout
        self.widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        self.widget.setLayout(layout)

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

        remove = QtGui.QToolButton()
        layout.addWidget(remove, 1, 101)
        remove.setIcon(self.widget.style().standardIcon(
            QtGui.QStyle.SP_TitleBarCloseButton
        ))
        remove.setStyleSheet("border: 0px;")
        remove.clicked.connect(self.remove_click)

        # attributes
        self.Qt_args = [routine]
        self.Qt_arglabels = [None]
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

    def args_init(self):
        """Initialize the arguments."""
        call = self.Qt_gui.calls[self.callid]
        Qroutine = self.Qt_args[0]
        Qroutine.setProperty("invalid", False)
        Qroutine.style().unpolish(Qroutine)
        Qroutine.style().polish(Qroutine)
        Qroutine.update()
        if isinstance(call, signature.Call):
            self.sig = call.sig
        else:
            minsig = self.Qt_gui.sampler["kernels"][call[0]]
            self.sig = None
            if not self.Qt_gui.nosigwarning_shown:
                self.Qt_gui.UI_alert("No signature found for %r!\n" % call[0] +
                                     "Hover arguments for input syntax.")
                self.Qt_gui.nosigwarning_shown = True
        doc = self.Qt_gui.docs_get(call[0])
        if doc:
            Qroutine.setToolTip(doc[0][1])
        for argid in range(len(call))[1:]:
            tooltip = ""
            if self.sig:
                argname = self.sig[argid].name
                if doc and argid < len(doc):
                    tooltip = doc[argid][1]
            else:
                argname = minsig[argid].replace("*", " *")
                if doc and argid < len(doc):
                    argname += doc[argid][0]
                    tooltip = doc[argid][1]
                if argname in ("int *", "float *", "double *"):
                    if doc:
                        tooltip += "\n\n*Format*:\n" if doc else ""
                    tooltip += ("Scalar:\tvalue\t\te.g. 1, -0.5\n"
                                "Array:\t[#elements]"
                                "\te.g. [10000] for a 100x100 matrix")
            Qarglabel = QtGui.QLabel(argname)
            if tooltip:
                Qarglabel.setToolTip(tooltip)
            self.widget.layout().addWidget(Qarglabel, 0, argid)
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
                Qarg = QtGui.QLineEdit(" ")
                Qarg.textChanged.connect(self.arg_change)
                if tooltip:
                    Qarg.setToolTip(tooltip)
            if tooltip:
                Qarg.setToolTip(tooltip)
            Qarg.argid = argid
            self.Qt_args.append(Qarg)
            self.arg_set(argid)
            self.widget.layout().addWidget(Qarg, 1, argid,
                                           QtCore.Qt.AlignCenter)
        if self.sig:
            self.showargs_apply()
        self.update_size()

    def args_clear(self):
        """Clear the arguments."""
        Qroutine = self.Qt_args[0]
        Qroutine.setProperty("invalid", True)
        Qroutine.style().unpolish(Qroutine)
        Qroutine.style().polish(Qroutine)
        Qroutine.update()
        for Qarg in self.Qt_args[1:]:
            Qarg.deleteLater()
        self.Qt_args = self.Qt_args[:1]
        for Qarglabel in self.Qt_arglabels[1:]:
            Qarglabel.deleteLater()
        self.Qt_arglabels = self.Qt_arglabels[:1]
        Qroutine.setToolTip("")
        self.update_size()
        self.sig = None

    def showargs_apply(self):
        """Apply which argument types are shown."""
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
                    showing = self.Qt_gui.showargs[name]
                    self.Qt_arglabels[argid].setVisible(showing)
                    self.Qt_args[argid].setVisible(showing)

    def arg_setvalid(self, argid):
        """Set the valid proparty for the argument."""
        self.Qt_gui.Qt_setting += 1
        val = self.Qt_gui.calls[self.callid][argid]
        Qarg = self.Qt_args[argid]
        Qarg.setProperty("invalid", val is None)
        Qarg.style().unpolish(Qarg)
        Qarg.style().polish(Qarg)
        Qarg.update()
        self.Qt_gui.Qt_setting -= 1

    def arg_set(self, argid):
        """Set an argument's value."""
        self.arg_setvalid(argid)
        self.Qt_gui.Qt_setting += 1
        val = self.Qt_gui.calls[self.callid][argid]
        Qarg = self.Qt_args[argid]
        val = "" if val is None else str(val)
        if isinstance(Qarg, QDataArg):
            Qarg.set()
        elif isinstance(Qarg, QtGui.QLineEdit):
            Qarg.setText(val)
        elif isinstance(Qarg, QtGui.QComboBox):
            Qarg.setCurrentIndex(Qarg.findText(val))
        self.Qt_gui.Qt_setting -= 1

    def args_set(self, fromargid=None):
        """set all arguments and their values."""
        self.Qt_gui.Qt_setting += 1
        call = self.Qt_gui.calls[self.callid]
        # set routine
        self.Qt_args[0].setText(call[0])
        # set widgets
        if call[0] not in self.Qt_gui.sampler["kernels"]:
            self.args_clear()
            self.Qt_gui.Qt_setting -= 1
            return
        if isinstance(call, signature.Call):
            if call.sig != self.sig:
                if len(self.Qt_args) > 1:
                    self.args_clear()
                self.args_init()
                self.Qt_gui.Qt_setting -= 1
                return
        else:
            if len(self.Qt_args) != len(call):
                if len(self.Qt_args) > 1:
                    self.args_clear()
                self.args_init()
                self.Qt_gui.Qt_setting -= 1
                return
        # otherwise: set values
        for argid in range(len(call)):
            if argid == fromargid:
                self.arg_setvalid(argid)
            else:
                self.arg_set(argid)
        self.update_size()
        self.Qt_gui.Qt_setting -= 1

    def data_viz(self):
        """Visualize all operands."""
        if not self.sig:
            return
        for argid in self.Qt_gui.calls[self.callid].sig.dataargs():
            self.Qt_args[argid].viz()
        self.update_size()

    # event handlers
    def remove_click(self):
        """Event: Remove call."""
        self.Qt_gui.UI_call_remove(self.callid)

    def arg_change(self):
        """Event: Changed an argument."""
        sender = self.Qt_gui.Qt_app.sender()
        if isinstance(sender, QtGui.QLineEdit):
            # adjust widt no matter where the change came from
            val = str(sender.text())
            if not isinstance(sender, QDataArg):
                width = sender.fontMetrics().width(val)
                width += sender.minimumSizeHint().width()
                width = min(width, sender.sizeHint().width())
                height = sender.sizeHint().height()
                if sender.argid == 0:
                    sender.setMinimumSize(max(height, width), height)
                else:
                    sender.setFixedSize(max(height, width), height)
        if self.Qt_gui.Qt_setting:
            return
        if isinstance(sender, QtGui.QComboBox):
            val = str(sender.currentText())
        if not val:
            val = None
        self.Qt_gui.UI_arg_change(self.callid, sender.argid, val)
