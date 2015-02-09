#!/usr/bin/env python
from __future__ import division, print_function

import symbolic

from PyQt4 import QtCore, QtGui


class QDataArg(QtGui.QLineEdit):
    def __init__(self, call):
        QtGui.QLineEdit.__init__(self)
        self.Qt_call = call
        self.Qt_gui = call.Qt_gui
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None

        self.UI_init()

    def UI_init(self):
        self.setAlignment(QtCore.Qt.AlignHCenter)
        self.textChanged.connect(self.change)
        self.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[a-zA-Z]+"),
                                                 self.Qt_gui.Qt_app))

        # self.setsize(0, 0)

        # style
        self.setStyleSheet("""
            [invalid="true"] {
                background: #FFDDDD;
            }
            [invalid="false"]:!focus:!hover {
                background: transparent;
                border: none;
            }
        """)

    def paintEvent(self, event):
        if not self.linesminfront:
            # nothing to draw
            return QtGui.QLineEdit.paintEvent(self, event)

        brushes = self.Qt_gui.Qt_brushes
        pens = self.Qt_gui.Qt_pens
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

        # draw input on top
        painter.end()
        return QtGui.QLineEdit.paintEvent(self, event)

    # setters
    def set(self):
        value = self.Qt_gui.calls[self.Qt_call.callid][self.argid]
        if value is None:
            value = ""
        self.setText(value)
        self.viz()

    def setsize(self, height, width):
        minsize = QtGui.QLineEdit().minimumSizeHint()
        fontmetrics = self.fontMetrics()
        minwidth = minsize.width() + fontmetrics.width(self.text())
        minheight = minsize.height()
        minwidth = max(minwidth, minheight)
        fixedwidth = max(width, minwidth)
        fixedheight = max(height, minheight)
        self.setFixedSize(fixedwidth, fixedheight)
        hoff = max(0, (minheight - height) // 2)
        woff = max(0, (minwidth - width) // 2)
        return hoff, woff

    def viz(self):
        value = self.Qt_gui.calls[self.Qt_call.callid][self.argid]
        if value is None:
            self.viz_none()
            return
        data = self.Qt_gui.data[value]
        if data["sym"] is None:
            self.viz_none()
            return
        if isinstance(data["sym"], symbolic.Prod):
            # we're good
            dim = data["sym"][1:]
        else:
            # try simplifying
            if isinstance(data["sym"], symbolic.Expression):
                sym = data["sym"].simplify()
            else:
                sym = data["sym"]
            if isinstance(sym, symbolic.Prod):
                dim = sym[1:]
            else:
                dim = [sym]
        # compute min and max from range
        dimmin = []
        dimmax = []
        for expr in dim:
            values = list(self.Qt_gui.range_eval(expr))
            if not values:
                self.viz_none()
                return
            if any(value is None for value in values):
                self.viz_none()
                return
            dimmin.append(min(values))
            dimmax.append(max(values))
        if len(dim) == 1:
            self.viz_vector(dimmin, dimmax)
        elif len(dim) == 2:
            self.viz_matrix(dimmin, dimmax)
        elif len(dim) == 3:
            self.viz_tensor(dimmin, dimmax)

    def viz_none(self):
        self.setsize(0, 0)
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None

    def viz_vector(self, dimmin, dimmax):
        self.viz_matrix(dimmin + [1], dimmax + [1])

    def viz_matrix(self, dimmin, dimmax):
        scale = self.Qt_gui.datascale / max(1, self.Qt_gui.data_maxdim())
        dimmin = [int(round(scale * dim)) for dim in dimmin]
        dimmax = [int(round(scale * dim)) for dim in dimmax]
        call = self.Qt_gui.calls[self.Qt_call.callid]
        properties = call.properties(self.argid)
        for prop in properties:
            if prop in ("lower", "upper"):
                self.viz_triangular(dimmin, dimmax, properties)
                return
        self.viz_tensor(dimmin + [1], dimmax + [1])

    def viz_triangular(self, dimmin, dimmax, properties):
        # compute total size and offsets
        h, w = dimmax
        hoff, woff = self.setsize(h + 1, w + 1)
        # maximum
        h, w = dimmax
        points = [[QtCore.QPoint(woff + x, hoff + y)
                   for x in [0, w]]
                  for y in [0, h]]
        if "lower" in properties:
            self.polygonmax = QtGui.QPolygon([
                points[0][0],
                points[1][0],
                points[1][1],
                points[0][0],
            ])
            self.linesmaxfront = [
                QtCore.QLine(points[0][0], points[1][0]),  # |
                QtCore.QLine(points[1][0], points[1][1]),  # -
                QtCore.QLine(points[1][1], points[0][0]),  # \
            ]
        else:
            self.polygonmax = QtGui.QPolygon([
                points[0][0],
                points[1][1],
                points[0][1],
                points[0][0],
            ])
            self.linesmaxfront = [
                QtCore.QLine(points[0][0], points[1][1]),  # \
                QtCore.QLine(points[1][1], points[0][1]),  # |
                QtCore.QLine(points[0][1], points[0][0]),  # -
            ]
        self.linesmaxback = []
        if "symm" in properties or "herm" in properties:
            self.linesmaxback = [
                QtCore.QLine(points[0][0], points[1][0]),  # |
                QtCore.QLine(points[1][0], points[1][1]),  # -
                QtCore.QLine(points[1][1], points[0][1]),  # |
                QtCore.QLine(points[0][1], points[0][0]),  # -
            ]
        # minimum
        h, w = dimmin
        points = [[QtCore.QPoint(woff + x, hoff + y)
                   for x in [0, w]]
                  for y in [0, h]]
        if "lower" in properties:
            self.polygonmin = QtGui.QPolygon([
                points[0][0],
                points[1][0],
                points[1][1],
                points[0][0],
            ])
            self.linesminfront = [
                QtCore.QLine(points[0][0], points[1][0]),  # |
                QtCore.QLine(points[1][0], points[1][1]),  # -
                QtCore.QLine(points[1][1], points[0][0]),  # \
            ]
        else:
            self.polygonmin = QtGui.QPolygon([
                points[0][0],
                points[1][1],
                points[0][1],
                points[0][0],
            ])
            self.linesminfront = [
                QtCore.QLine(points[0][0], points[1][1]),  # \
                QtCore.QLine(points[1][1], points[0][1]),  # |
                QtCore.QLine(points[0][1], points[0][0]),  # -
            ]
        self.linesminback = []
        if "symm" in properties or "herm" in properties:
            self.linesminback = [
                QtCore.QLine(points[0][0], points[1][0]),  # |
                QtCore.QLine(points[1][0], points[1][1]),  # -
                QtCore.QLine(points[1][1], points[0][1]),  # |
                QtCore.QLine(points[0][1], points[0][0]),  # -
            ]

    def viz_tensor(self, dimmin, dimmax):
        # compute total size and offsets
        h, w, d = dimmax
        hoff, woff = self.setsize(h + d // 2 + 1, w + d // 2 + 1)
        # maximum
        h, w, d = dimmax
        points = [[[QtCore.QPoint(woff + x + z // 2, hoff + y + (d - z) // 2)
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
        if d != 0:
            self.linesmaxback = []
        # minimum
        h, w, d = dimmin
        points = [[[QtCore.QPoint(woff + x + z // 2, hoff + y + (d - z) // 2)
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

    # event handlers
    def change(self):
        if self.Qt_gui.Qt_setting:
            return
        value = str(self.text())
        self.Qt_gui.UI_arg_change(self.Qt_call.callid, self.argid, value)
