#!/usr/bin/env python
from __future__ import division, print_function

from PyQt4 import QtGui
import matplotlib.backends.backend_qt4agg as QtMPL
import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines


class QMPLplot(QtGui.QWidget):
    def __init__(self, app, metric):
        QtGui.QWidget.__init__(self)
        self.metric = metric
        self.app = app

        self.setting = False
        self.fig_init()
        self.plottypes_init()
        self.UI_init()

    def fig_init(self):
        self.fig = MPLfig.Figure()
        self.axes = self.fig.add_subplot(111)  # TODO: 111 necessary?

    def plottypes_init(self):
        def med(data):
            sorteddata = sorted(data)
            datalen = len(sorteddata)
            mid = (datalen - 1) // 2
            if datalen % 2 == 0:
                return sorteddata[mid]
            return (sorteddata[mid] + sorteddata[mid + 1]) / 2
        self.plottypes = {
            "med": med,
            "min": min,
            "max": max,
            "avg": lambda data: sum(data) / len(data),
            "all": lambda data: data
        }
        self.plottype_styles = {
            "legend": {"linestyle": "-"},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":"},
            "avg": {"linestyle": "-."},
            "all": {"linestyle": "None", "marker": "."},
            "minmax": {"alpha": .25},
        }

        self.plottypes_showing = set(["med"])

    def UI_init(self):
        self.setWindowTitle(self.metric)

        # layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # canvas
        self.Qcanvas = QtMPL.FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.Qcanvas, 1)

        # toolbar
        toolbar = QtMPL.NavigationToolbar2QT(self.Qcanvas, self)
        layout.addWidget(toolbar)

        # plottypes
        plottypesbox = QtGui.QWidget()
        layout.addWidget(plottypesbox)
        plottypesL = QtGui.QHBoxLayout()
        plottypesbox.setLayout(plottypesL)
        plottypesL.addStretch(1)
        plottypesL.addWidget(QtGui.QLabel("statistics:"))
        self.Qplottypes = {}
        for plottype in ("med", "min", "avg", "max", "all"):
            plottype_showing = QtGui.QCheckBox(plottype)
            plottypesL.addWidget(plottype_showing)
            plottype_showing.setChecked(plottype in self.plottypes_showing)
            plottype_showing.stateChanged.connect(self.plottype_changed)
            plottype_showing.plottype = plottype
        plottypesL.addStretch(1)

    def plot_update(self):
        # prepare data
        data = {}
        rangevarnames = set()
        rangevals = set()
        for reportid, report in enumerate(self.app.reports):
            for callid, state in report["plotting"].iteritems():
                if not report["plotting"][callid]:
                    continue
                if report["userange"]:
                    rangevarnames.add(report["rangevar"])
                rawdata = self.app.generateplotdata(reportid, callid,
                                                    self.metric)
                if not rawdata:
                    continue
                rangevals.update(zip(*rawdata)[0])
                linedatas = {
                    plottype: [(x, self.plottypes[plottype](y))
                               for x, y in rawdata
                               if y is not None]
                    for plottype in self.plottypes_showing
                }
                if "all" in linedatas:
                    linedatas["all"] = [(x, y) for x, ys in linedatas["all"]
                                        for y in ys]
                if "min" in linedatas and "max" in linedatas:
                    linedatas["minmax"] = [
                        p1 + (p2[1],) for p1, p2 in zip(linedatas["min"],
                                                        linedatas["max"])
                    ]
                    del linedatas["min"]
                    del linedatas["max"]
                data[reportid, callid] = linedatas
        rangevarname = " = ".join(rangevarnames)

        # set up pseudo range for reports without range
        rangevals.discard(None)
        if rangevals:
            rangemin = min(rangevals)
            rangemax = max(rangevals)
        else:
            # TODO: use barplot
            rangemin = 0
            rangemax = 1
        for linedatas in data.values():
            for linedata in linedatas.values():
                for i, (x, y) in enumerate(linedata[:]):
                    if x is None:
                        linedata += [(rangemin, y), (rangemax, y)]
                        del linedata[i]

        # set up figure
        self.axes.cla()
        self.axes.set_xlabel(rangevarname)
        self.axes.set_ylabel(self.metric)
        self.axes.hold(True)

        # add plots
        legend = []
        for (reportid, callid), linedatas in data.iteritems():
            report = self.app.reports[reportid]
            color = report["plotcolors"][callid]
            legendlabel = report["name"]
            if callid is not None:
                legendlabel += " (%s)" % str(report["calls"][callid][0])
            legend.append((MPLlines.Line2D([], [], color=color,
                                           **self.plottype_styles["legend"]),
                           legendlabel))
            for plottype, linedata in linedatas.iteritems():
                if plottype == "minmax":
                    x, y1, y2 = zip(*linedata)
                    self.axes.fill_between(x, y1, y2, color=color,
                                           **self.plottype_styles[plottype])
                else:
                    x, y = zip(*linedata)
                    self.axes.plot(x, y, color=color,
                                   **self.plottype_styles[plottype])
        if legend:
            # artists, labels = zip(*legend)
            self.axes.legend(*zip(*legend))
        self.Qcanvas.draw()

    # event handers
    def plottype_changed(self):
        sender = self.app.sender()
        if sender.isChecked():
            self.plottypes_showing.add(sender.plottype)
        else:
            self.plottypes_showing.discard(sender.plottype)
        self.plot_update()
