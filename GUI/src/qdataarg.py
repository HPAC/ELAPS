#!/usr/bin/env python
from __future__ import division, print_function

import symbolic

from PyQt4 import QtCore, QtGui


class QDataArg(QtGui.QWidget):
    def __init__(self, call):
        QtGui.QFrame.__init__(self)
        self.call = call
        self.app = call.app
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None

        self.UI_init()

    def UI_init(self):
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        # name
        self.name = QtGui.QLineEdit()
        layout.addWidget(self.name, alignment=QtCore.Qt.AlignHCenter)
        self.name.setAlignment(QtCore.Qt.AlignHCenter)
        self.name.setContentsMargins(0, 0, 0, 0)
        self.name.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
        ))
        self.name.textChanged.connect(self.change)
        regexp = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(regexp, self.app)
        self.name.setValidator(validator)

        # style
        self.setStyleSheet("""
            [invalid="true"] QLineEdit {
                background: #FFDDDD;
            }
            [invalid="false"] > QLineEdit:!focus:!hover {
                background: transparent;
                border: none;
            }
        """)

    def paintEvent(self, event):
        if not self.polygonmax:
            return QtGui.QFrame.paintEvent(self, event)

        brushes = self.app.Qt_brushes
        pens = self.app.Qt_pens
        painter = QtGui.QPainter(self)

        # max
        painter.setBrush(brushes["max"])
        painter.setPen(pens[None])
        painter.drawPolygon(self.polygonmax)
        painter.setPen(pens["maxback"])
        painter.drawLines(self.linesmaxback)
        painter.setPen(pens["maxfront"])
        painter.drawLines(self.linesmaxfront)

        # min
        painter.setBrush(brushes["min"])
        painter.setPen(pens[None])
        painter.drawPolygon(self.polygonmin)
        painter.setPen(pens["minback"])
        painter.drawLines(self.linesminback)
        painter.setPen(pens["minfront"])
        painter.drawLines(self.linesminfront)

    def set(self):
        value = self.app.calls[self.call.callid][self.argid]
        if value is None:
            value = ""
        self.name.setText(value)
        self.viz()

    def viz(self):
        value = self.app.calls[self.call.callid][self.argid]
        if value is None:
            self.viz_none()
            return
        data = self.app.data[value]
        if not isinstance(data["sym"], symbolic.Prod):
            # TODO
            self.app.alert("don't know how to vizualize", data["sym"])
            self.viz_none()
            return
        # compute min and max from range
        scale = self.app.state["datascale"] / self.app.data_maxdim()
        dim = data["sym"][1:]
        dimmin = []
        dimmax = []
        for expr in dim:
            values = self.app.range_eval(expr)
            if any(value is None for value in values):
                self.viz_none()
                return
            dimmin.append(round(scale * min(values)))
            dimmax.append(round(scale * max(values)))
        if len(dim) == 1:
            self.viz_vector(dimmin, dimmax)
        elif len(dim) == 2:
            self.viz_matrix(dimmin, dimmax)
        elif len(dim) == 3:
            self.viz_tensor(dimmin, dimmax)

    def viz_none(self):
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None
        self.setMinimumSize(self.name.minimumSize())

    def viz_vector(self, dimmin, dimmax):
        self.viz_matrix(dimmin + [1], dimmax + [1])

    def viz_matrix(self, dimmin, dimmax):
        self.viz_tensor(dimmin + [1], dimmax + [1])

    def viz_tensor(self, dimmin, dimmax):
        # compute total size and offsets
        h, w, d = dimmax
        screenheight = h + d // 2 + 1
        screenwidth = w + d // 2 + 1
        inputheight = self.name.minimumSizeHint().height()
        inputwidth = self.name.minimumSizeHint().width()
        self.setFixedSize(
            max(screenwidth, inputwidth),
            max(screenheight, inputheight)
        )
        yoff = max(0, (inputheight - screenheight) // 2)
        xoff = max(0, (inputwidth - screenwidth) // 2)
        # maximum
        h, w, d = dimmax
        points = [[[QtCore.QPoint(xoff + x + z // 2, yoff + y + z // 2)
                    for z in [0, d]]
                   for x in [0, w]]
                  for y in [0, h]]
        self.polygonmax = QtGui.QPolygon([
            points[0][0][0],
            points[1][0][0],
            points[1][1][0],
            points[1][1][1],
            points[0][1][1],
            points[0][0][1],
        ])
        self.linesmaxfront = [
            QtCore.QLine(points[0][0][0], points[0][0][1]),  # /
            QtCore.QLine(points[0][1][0], points[0][1][1]),  # /
            QtCore.QLine(points[1][1][0], points[1][1][1]),  # /
            QtCore.QLine(points[0][0][0], points[0][1][0]),  # -
            QtCore.QLine(points[0][0][1], points[0][1][1]),  # -
            QtCore.QLine(points[1][0][0], points[1][1][0]),  # -
            QtCore.QLine(points[0][0][0], points[1][0][0]),  # |
            QtCore.QLine(points[0][1][0], points[1][1][0]),  # |
            QtCore.QLine(points[0][1][1], points[1][1][1]),  # |
        ]
        self.linesmaxback = [
            QtCore.QLine(points[1][0][0], points[1][0][1]),  # /
            QtCore.QLine(points[1][0][1], points[1][1][1]),  # -
            QtCore.QLine(points[0][0][1], points[1][0][1]),  # |
        ]
        # minimum
        h, w, d = dimmin
        points = [[[QtCore.QPoint(xoff + x + z // 2, yoff + y + z // 2)
                    for z in [0, d]]
                   for x in [0, w]]
                  for y in [0, h]]
        self.polygonmin = QtGui.QPolygon([
            points[0][0][0],
            points[1][0][0],
            points[1][1][0],
            points[1][1][1],
            points[0][1][1],
            points[0][0][1],
        ])
        self.linesminfront = [
            QtCore.QLine(points[0][0][0], points[0][0][1]),  # /
            QtCore.QLine(points[0][1][0], points[0][1][1]),  # /
            QtCore.QLine(points[1][1][0], points[1][1][1]),  # /
            QtCore.QLine(points[0][0][0], points[0][1][0]),  # -
            QtCore.QLine(points[0][0][1], points[0][1][1]),  # -
            QtCore.QLine(points[1][0][0], points[1][1][0]),  # -
            QtCore.QLine(points[0][0][0], points[1][0][0]),  # |
            QtCore.QLine(points[0][1][0], points[1][1][0]),  # |
            QtCore.QLine(points[0][1][1], points[1][1][1]),  # |
        ]
        self.linesminback = [
            QtCore.QLine(points[1][0][0], points[1][0][1]),  # /
            QtCore.QLine(points[1][0][1], points[1][1][1]),  # -
            QtCore.QLine(points[0][0][1], points[1][0][1]),  # |
        ]

    def text(self):
        return self.name.text()

    def change(self):
        if self.app.setting:
            return
        val = str(self.name.text())
        self.call.app.UI_arg_change(self.call.callid, self.argid, val)
