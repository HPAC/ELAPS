#!/usr/bin/env python
from __future__ import division, print_function

from PyQt4 import QtCore, QtGui


class QDataArg(QtGui.QFrame):
    def __init__(self, call):
        QtGui.QFrame.__init__(self)
        self.call = call
        self.app = call.app
        self.dimmin = []
        self.dimmax = []
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None

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
        name = self.app.state["calls"][self.call.callid][self.argid]
        sizehint = self.name.minimumSizeHint()
        if name is None:
            self.name.setText("")
            self.dim.setText("")
            return
        self.name.setText(name)
        data = self.app.data[name]
        self.dimmin = data["dimmin"]
        self.dimmax = data["dimmax"]
        # TODO: handle exceptions
        if len(self.dimmax) <= 3 and all(self.dimmin + self.dimmax):
            # compute 3D sizes
            scale = self.app.state["datascale"] / self.app.data_maxdim()
            drawmax = [int(scale * d) for d in self.dimmax]
            drawmax += (3 - len(self.dimmin)) * [0]
            drawmin = [int(scale * d) for d in self.dimmin]
            drawmin += (3 - len(self.dimmin)) * [0]
            # compute total size and offsets
            h, w, d = drawmax
            screenheight = h + d // 2 + 1
            screenwidth = w + d // 2 + 1
            inputheight = self.name.sizeHint().height()
            inputwidth = self.name.minimumSizeHint().width()
            self.setFixedSize(
                max(screenwidth, inputwidth),
                max(screenheight, inputheight)
            )
            yoff = max(0, (inputheight - screenheight) // 2)
            xoff = max(0, (inputwidth - screenwidth) // 2)
            # maximum
            h, w, d = drawmax
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
            h, w, d = drawmin
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
        else:
            self.polygonmax = None
            self.linesmaxfront = None
            self.linesmaxback = None
            self.polygonmin = None
            self.linesminfront = None
            self.linesminback = None
            self.setMinimumSize(0, 0)
            heiht = width = 0

    def text(self):
        return self.name.text()

    def change(self):
        if self.app.setting:
            return
        val = str(self.name.text())
        self.call.app.UI_arg_change(self.call.callid, self.argid, val)
