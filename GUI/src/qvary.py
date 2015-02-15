#!/usr/bin/env python
"""Options for how one data argument varies."""
from __future__ import division, print_function

import symbolic

from PyQt4 import QtCore, QtGui


class QVary(QtGui.QGroupBox):

    """Options for how a named data argument varies."""

    def __init__(self, gui, name):
        """Initialize the options."""
        QtGui.QGroupBox.__init__(self, "vary " + name)
        self.Qt_gui = gui
        self.name = name

        self.UI_init()

    def UI_init(self):
        """Initialize the GUI elements."""
        self.setCheckable(True)
        self.toggled.connect(self.Qt_toggled)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # across
        self.Qt_across = QtGui.QGroupBox("across")
        layout.addWidget(self.Qt_across)
        acrossL = QtGui.QVBoxLayout()
        self.Qt_across.setLayout(acrossL)
        self.Qt_Qacross = {}
        for across, desc in (
            ("reps", "repetitions"),
            ("sum", "summation"),
            ("omp", "parallel range")
        ):
            Qacross = QtGui.QCheckBox(desc)
            acrossL.addWidget(Qacross)
            Qacross.stateChanged.connect(self.Qt_across_change)
            Qacross.across = across
            self.Qt_Qacross[across] = Qacross

        # along
        alongL = QtGui.QHBoxLayout()
        layout.addLayout(alongL)
        self.Qt_alonglabel = QtGui.QLabel("along: ")
        alongL.addWidget(self.Qt_alonglabel, 0, QtCore.Qt.AlignBottom)
        self.Qt_Qalong = []
        for i, label in enumerate((
            QtGui.QStyle.SP_ToolBarVerticalExtensionButton,
            QtGui.QStyle.SP_ToolBarHorizontalExtensionButton,
            "depth"
        )):
            along = QtGui.QRadioButton("")
            if isinstance(label, str):
                along.setText(label)
            else:
                along.setIcon(along.style().standardIcon(label))
            alongL.addWidget(along)
            along.toggled.connect(self.Qt_along_toggle)
            along.dim = i
            self.Qt_Qalong.append(along)
        alongL.addStretch(1)

        offsetL = QtGui.QHBoxLayout()
        layout.addLayout(offsetL)
        self.Qt_offsetlabel = QtGui.QLabel("offset:")
        offsetL.addWidget(self.Qt_offsetlabel)
        self.Qt_offset = QtGui.QLineEdit()
        offsetL.addWidget(self.Qt_offset)
        self.Qt_offset.textChanged.connect(self.Qt_offset_change)
        offsetL.addStretch(1)

        layout.addStretch(1)

    def set(self):
        """Set all options."""
        self.Qt_gui.Qt_setting += 1
        if self.name not in self.Qt_gui.vary:
            self.setChecked(False)
            for widget in ([self.Qt_across, self.Qt_alonglabel,
                            self.Qt_offsetlabel, self.Qt_offset] +
                           self.Qt_Qalong):
                widget.hide()
            self.Qt_gui.Qt_setting -= 1
            return
        data = self.Qt_gui.data[self.name]
        vary = self.Qt_gui.vary[self.name]

        # across
        innerrange = self.Qt_gui.userange["inner"]
        self.Qt_across.setVisible(innerrange is not None)
        for across, Qacross in self.Qt_Qacross.iteritems():
            Qacross.setVisible(across == "reps" or across == innerrange)
            Qacross.setChecked(across in vary["across"])

        # along
        self.Qt_alonglabel.show()
        self.Qt_Qalong[0].show()
        self.Qt_Qalong[1].show()
        if isinstance(data["dims"], symbolic.Prod):
            self.Qt_Qalong[2].setVisible(len(data["dims"]) > 3)
        else:
            self.Qt_Qalong[2].hide()
        for i, Qalong in enumerate(self.Qt_Qalong):
            Qalong.setChecked(i == vary["along"])
        self.Qt_gui.Qt_setting -= 1

        # offset
        self.Qt_offsetlabel.show()
        self.Qt_offset.show()
        self.Qt_offset.setText(str(vary["offset"]))

        self.adjustSize()

    # event handlers
    def Qt_toggled(self, on):
        """En/disabled the vary."""
        if self.Qt_gui.Qt_setting:
            return
        self.Qt_gui.UI_vary_change(self.name, on)

    def Qt_across_change(self):
        """Changed across wich loops to vary."""
        if self.Qt_gui.Qt_setting:
            return
        sender = self.Qt_gui.Qt_app.sender()
        vary = self.Qt_gui.vary[self.name].copy()
        vary["across"] = vary["across"].copy()
        if sender.isChecked():
            vary["across"].add(sender.across)
        else:
            vary["across"].discard(sender.across)
        self.Qt_gui.UI_vary_change(self.name, vary)

    def Qt_along_toggle(self):
        """Changed across wich dimensions to vary."""
        if self.Qt_gui.Qt_setting:
            return
        sender = self.Qt_gui.Qt_app.sender()
        if not sender.isChecked():
            return
        vary = self.Qt_gui.vary[self.name].copy()
        vary["along"] = sender.dim
        self.Qt_gui.UI_vary_change(self.name, vary)

    def Qt_offset_change(self):
        """Changed the manual offset."""
        value = str(self.Qt_offset.text())
        width = self.Qt_offset.fontMetrics().width(value)
        width += self.Qt_offset.minimumSizeHint().width()
        height = self.Qt_offset.sizeHint().height()
        self.Qt_offset.setFixedSize(max(height, width), height)
        if self.Qt_gui.Qt_setting:
            return
        vary = self.Qt_gui.vary[self.name].copy()
        try:
            vary["offset"] = int(vary)
            self.Qt_gui.UI_vary_change(self.name, vary)
        except:
            # TODO: alert
            pass
