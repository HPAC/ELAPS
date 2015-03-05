#!/usr/bin/env python
"""Representation of data arguments in QCalls in ELAPS:PlayMat."""
from __future__ import division, print_function

from elaps import symbolic

from PyQt4 import QtCore, QtGui


class QDataArg(QtGui.QLineEdit):

    """Operand argument representation."""

    def __init__(self, UI_call, *args, **kwargs):
        """Initialize the operand representation."""
        QtGui.QLineEdit.__init__(self, *args, **kwargs)
        self.UI_call = UI_call
        self.playmat = UI_call.playmat
        self.offsetstr = None
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None

        self.UI_init()

    @property
    def call(self):
        """Get the call."""
        return self.UI_call.call

    def UI_init(self):
        """Initialize the GUI element."""
        self.setAlignment(QtCore.Qt.AlignHCenter)
        self.setValidator(QtGui.QRegExpValidator(
            QtCore.QRegExp("[a-zA-Z][a-zA-Z0-9_]*"), self
        ))

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
        """Paint the representation."""
        if not self.linesminfront:
            # nothing to draw
            return QtGui.QLineEdit.paintEvent(self, event)

        brushes = self.playmat.brushes
        pens = self.playmat.pens
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

        # offset
        if self.offsetstr:
            painter.drawText(
                QtCore.QRect(2, 2, self.width() - 4, self.height() - 4),
                QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight,
                self.offsetstr
            )

        # draw input on top
        painter.end()
        return QtGui.QLineEdit.paintEvent(self, event)

    # setters
    def setsize(self, height, width):
        """Set the size of the widget."""
        minsizehint = QtGui.QLineEdit().minimumSizeHint()
        sizehint = QtGui.QLineEdit().minimumSizeHint()
        fontmetrics = self.fontMetrics()

        minheight = minsizehint.height()
        minwidth = minsizehint.width() + fontmetrics.width(self.text())
        minwidth = max(minwidth, minheight)
        if self.offsetstr:
            minheight += 2 * fontmetrics.height() + 8
            minwidth = max(minwidth, fontmetrics.width(self.offsetstr))

        fixedwidth = max(width, minwidth)
        fixedheight = max(height, minheight)
        self.setFixedSize(fixedwidth, fixedheight)

        hoff = max(0, (minheight - height) // 2)
        woff = max(0, (minwidth - width) // 2)
        return hoff, woff

    def viz(self):
        """Visualization update."""
        call = self.call
        value = call[self.argid]
        ex = self.playmat.experiment
        if value not in ex.data:
            self.viz_none()
            return
        data = ex.data[value]

        # vary
        dims = data["dims"]
        vary = data["vary"]
        self.offsetstr = None
        if vary["with"]:
            if len(dims) > 1:
                if vary["along"] < 3:
                    self.offsetstr = u"\u2193\u2192\u2197"[vary["along"]]
                else:
                    self.offsetstr = str(vary["along"])
            self.offsetstr += " (%s)" % ", ".join(vary["with"])
            if vary["offset"]:
                self.offsetstr += " + %s" % vary["offset"]

        # compute min and max from range
        dimmin = []
        dimmax = []
        for expr in dims:
            rangemin, rangemax = ex.ranges_eval_minmax(expr)
            if rangemin is None or rangemax is None:
                self.viz_none()
                return
            dimmin.append(rangemin)
            dimmax.append(rangemax)
        if float("inf") in dimmin or -float("inf") in dimmax:
            self.viz_none()
            return
        if "work" in call.properties(self.argid):
            # maximum height for work
            maxdim = max(1, ex.data_maxdim())
            if dimmax[0] > maxdim:
                dims = [0, 0]
                dimmin = [maxdim, dimmin[0] // maxdim]
                dimmax = [maxdim, dimmax[0] // maxdim]
        if len(dims) == 1:
            self.viz_vector(dimmin, dimmax)
        elif len(dims) == 2:
            self.viz_matrix(dimmin, dimmax)
        elif len(dims) == 3:
            self.viz_tensor(dimmin, dimmax)

    def viz_none(self):
        """Empty visualization."""
        self.setsize(0, 0)
        self.offsetstr = None
        self.polygonmax = None
        self.linesmaxfront = None
        self.linesmaxback = None
        self.polygonmin = None
        self.linesminfront = None
        self.linesminback = None

    def viz_vector(self, dimmin, dimmax):
        """Vizualize a vector."""
        self.viz_matrix(dimmin + [1], dimmax + [1])

    def viz_matrix(self, dimmin, dimmax):
        """Visualize a matrix."""
        scale = (self.playmat.datascale /
                 max(1, self.playmat.experiment.data_maxdim()))
        dimmin = [int(round(scale * dim)) for dim in dimmin]
        dimmax = [int(round(scale * dim)) for dim in dimmax]
        call = self.playmat.experiment.calls[self.UI_call.callid]
        properties = call.properties(self.argid)
        for prop in properties:
            if prop in ("lower", "upper"):
                self.viz_triangular(dimmin, dimmax, properties)
                return
        self.viz_tensor(dimmin + [1], dimmax + [1])

    def viz_triangular(self, dimmin, dimmax, properties):
        """Visualize a triangular matrix."""
        # compute total size and offsets
        h, w = dimmax
        hoff, woff = self.setsize(h + 1, w + 1)
        # maximum
        h, w = dimmax
        points = [[QtCore.QPoint(woff + x, hoff + y)
                   for x in (0, w)]
                  for y in (0, h)]
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
                   for x in (0, w)]
                  for y in (0, h)]
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
        """Visualize a Tensor."""
        # compute total size and offsets
        h, w, d = dimmax
        hoff, woff = self.setsize(h + d // 2 + 1, w + d // 2 + 1)
        # maximum
        h, w, d = dimmax
        points = [[[QtCore.QPoint(woff + x + z // 2, hoff + y + (d - z) // 2)
                    for z in (0, d)]
                   for x in (0, w)]
                  for y in (0, h)]
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
                    for z in (0, d)]
                   for x in (0, w)]
                  for y in (0, h)]
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
